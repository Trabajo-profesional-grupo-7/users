import unittest

from pydantic import ValidationError

from app.schemas.chat import Chat


class TestChatSchema(unittest.TestCase):

    def test_create_valid_chat_instance(self):
        chat_data = {
            "user_id": 1,
            "thread_id": "thread_id",
            "assistant_id": "assistant__id",
        }

        chat_instance = Chat(**chat_data)

        self.assertEqual(chat_instance.user_id, 1)
        self.assertEqual(chat_instance.thread_id, "thread_id")
        self.assertEqual(chat_instance.assistant_id, "assistant__id")

    def test_missing_required_fields(self):
        chat_data = {"thread_id": "thread_id", "assistant_id": "assistant__id"}

        with self.assertRaises(ValidationError):
            Chat(**chat_data)

    def test_invalid_data_types(self):
        chat_data = {
            "user_id": "1",  # int
            "thread_id": 123,  # str
            "assistant_id": "assistant__id",
        }

        with self.assertRaises(ValidationError):
            Chat(**chat_data)
