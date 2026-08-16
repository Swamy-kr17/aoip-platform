import unittest

from schemas.chat_schema import Message
from services.task_analyzer import TaskAnalyzer


class TaskAnalyzerTests(unittest.TestCase):
    def assert_task(self, content, expected_task):
        messages = [Message(role="user", content=content)]

        self.assertEqual(TaskAnalyzer().analyze(messages), expected_task)

    def test_capital_does_not_match_api_substring(self):
        self.assert_task("What is the capital of France?", "general")

    def test_python_function_is_coding(self):
        self.assert_task("Write a Python function.", "coding")

    def test_api_is_coding(self):
        self.assert_task("What is an API?", "coding")

    def test_kannada_translation_is_translation(self):
        self.assert_task("Translate Good Morning to Kannada.", "translation")

    def test_article_keeps_writing_priority_over_summarization(self):
        self.assert_task("Summarize this article.", "writing")

    def test_write_email_is_writing(self):
        self.assert_task("Write an email to my professor.", "writing")

    def test_python_keeps_coding_priority_over_reasoning(self):
        self.assert_task("Why is Python popular?", "coding")


if __name__ == "__main__":
    unittest.main()
