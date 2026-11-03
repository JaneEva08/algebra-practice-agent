"""Author-written tasks; no pupil data and no textbook exercise numbers."""
TASKS = {
    ("equations", "easy"): {"id": "eq-e1", "question": "Реши уравнение x + 3 = 10.", "answer": "x = 7"},
    ("equations", "medium"): {"id": "eq-m1", "question": "Реши уравнение 3x - 5 = 10.", "answer": "x = 5"},
    ("equations", "hard"): {"id": "eq-h1", "question": "Реши уравнение 2(x - 3) = x + 5.", "answer": "x = 11"},
    ("brackets", "easy"): {"id": "br-e1", "question": "Раскрой скобки: -(a - 4).", "answer": "-a + 4"},
    ("brackets", "medium"): {"id": "br-m1", "question": "Упрости: 3(x - 2) - 2x.", "answer": "x - 6"},
    ("brackets", "hard"): {"id": "br-h1", "question": "Упрости: -2(3x - 4) + 3(2x - 5).", "answer": "-7"},
}


def select_task(topic: str, difficulty: str) -> dict:
    row = TASKS.get((topic, difficulty))
    if row is None:
        return {"error": "Такого сочетания нет в наборе.", "topics": ["equations", "brackets"],
                "difficulties": ["easy", "medium", "hard"]}
    # The answer key is deliberately not returned to the agent.
    return {"id": row["id"], "topic": topic, "difficulty": difficulty, "question": row["question"]}
