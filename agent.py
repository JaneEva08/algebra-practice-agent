"""LangChain create_agent + one custom tool + thread-scoped in-memory state."""
import argparse
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver

from tasks import select_task

ROOT = Path(__file__).resolve().parent


@tool
def get_practice_task(topic: str, difficulty: str) -> dict:
    """Get a checked algebra task. topic: equations or brackets.

    difficulty: easy, medium or hard. Return the exact task, never its answer.
    Use this tool whenever the student requests an exercise.
    """
    return select_task(topic, difficulty)


def make_agent():
    load_dotenv(ROOT / ".env")
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("Заполни OPENAI_API_KEY в локальном .env.")
    model = ChatOpenAI(model=os.getenv("CHAT_MODEL", "gpt-6-luna"),
                       api_key=os.environ["OPENAI_API_KEY"],
                       base_url=os.getenv("OPENAI_BASE_URL") or None,
                       timeout=90, max_retries=1, use_responses_api=False)
    return create_agent(model=model, tools=[get_practice_task], checkpointer=InMemorySaver(),
                        system_prompt="""Ты преподаватель алгебры для 7 класса. Пиши по-русски.
Для запроса упражнения обязательно используй get_practice_task.
Предлагай только точное условие из инструмента, укажи его ID и жди попытки.
Не показывай ответ или ход решения до попытки. Не придумывай номера учебника.
Если ученица просит сложнее, сохрани тему прежнего задания из истории,
увеличь сложность на один уровень и снова вызови инструмент.
Если инструмент не нашёл задачу, честно сообщи и предложи доступные темы.
Не называй задачу решённой, пока ученица не прислала ответ.""")


def run_demo():
    agent = make_agent()
    config = {"configurable": {"thread_id": "demo-student-one"}, "recursion_limit": 8}
    prompts = ["Дай простое упражнение на линейные уравнения.", "Дай сложнее по той же теме."]
    records = []
    previous_count = 0
    for prompt in prompts:
        result = agent.invoke({"messages": [{"role": "user", "content": prompt}]}, config)
        messages = result["messages"][previous_count:]
        calls = [call for msg in messages for call in getattr(msg, "tool_calls", [])]
        results = [{"name": msg.name, "content": msg.content} for msg in messages if msg.type == "tool"]
        answer = result["messages"][-1].content
        records.append({"prompt": prompt, "tool_calls": calls, "tool_results": results, "answer": answer})
        previous_count = len(result["messages"])
        print(prompt, "\n", json.dumps(calls, ensure_ascii=False), "\n", answer, flush=True)
        if not calls or not results:
            raise RuntimeError("Вызов инструмента не подтверждён.")
    expected = [select_task("equations", "easy"), select_task("equations", "medium")]
    for record, task in zip(records, expected):
        observed = [json.loads(item["content"]) for item in record["tool_results"]]
        if task not in observed:
            raise RuntimeError("Агент выбрал неожиданное упражнение; проверь результат.")
    (ROOT / "results").mkdir(exist_ok=True)
    (ROOT / "results/demo.json").write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", action="store_true")
    args = parser.parse_args()
    if args.demo:
        run_demo()
    else:
        agent = make_agent()
        config = {"configurable": {"thread_id": "local-student"}, "recursion_limit": 8}
        print("Преподаватель: напиши запрос упражнения. Выход: /exit")
        while True:
            prompt = input("> ").strip()
            if prompt == "/exit":
                break
            if prompt:
                result = agent.invoke({"messages": [{"role": "user", "content": prompt}]}, config)
                print(result["messages"][-1].content)
