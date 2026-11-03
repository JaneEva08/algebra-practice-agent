import unittest
from agent import get_practice_task
from tasks import TASKS, select_task


class ToolTests(unittest.TestCase):
    def test_tool_excludes_answer_key(self):
        for topic, level in TASKS:
            result = get_practice_task.invoke({"topic": topic, "difficulty": level})
            self.assertIn("question", result)
            self.assertNotIn("answer", result)

    def test_level_changes_task_but_not_topic(self):
        easy = select_task("equations", "easy")
        medium = select_task("equations", "medium")
        self.assertNotEqual(easy["id"], medium["id"])
        self.assertEqual(easy["topic"], medium["topic"])

    def test_unknown_request_does_not_invent_task(self):
        for topic, level in [("history", "easy"), ("equations", "impossible")]:
            result = get_practice_task.invoke({"topic": topic, "difficulty": level})
            self.assertIn("error", result)
            self.assertNotIn("question", result)


if __name__ == "__main__":
    unittest.main()
