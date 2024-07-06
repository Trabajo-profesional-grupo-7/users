import unittest
from datetime import datetime

from pydantic import ValidationError

from app.schemas.token import FcmToken, Token


class TestToken(unittest.TestCase):

    def test_valid_instance(self):
        data = {
            "token": "valid_token",
            "refresh_token": "valid_refresh_token",
            "token_type": "bearer",
        }

        token = Token(**data)

        self.assertEqual(token.token, "valid_token")
        self.assertEqual(token.refresh_token, "valid_refresh_token")
        self.assertEqual(token.token_type, "bearer")

    def test_missing_field(self):
        data = {"token": "valid_token", "token_type": "bearer"}

        with self.assertRaises(ValidationError):
            Token(**data)

    def test_invalid_token_type(self):
        data = {
            "token": "valid_token",
            "refresh_token": "valid_refresh_token",
            "token_type": 12345,
        }

        with self.assertRaises(ValidationError):
            Token(**data)


class TestFcmToken(unittest.TestCase):

    def test_valid_fcm_token(self):
        data = {"user_id": 1, "fcm_token": "valid_fcm_token"}

        fcm_token = FcmToken(**data)

        self.assertEqual(fcm_token.user_id, 1)
        self.assertEqual(fcm_token.fcm_token, "valid_fcm_token")

    def test_missing_user_id(self):
        data = {"fcm_token": "valid_fcm_token"}

        with self.assertRaises(ValidationError):
            FcmToken(**data)

    def test_invalid_user_id(self):
        data = {"user_id": "invalid_id", "fcm_token": "valid_fcm_token"}

        with self.assertRaises(ValidationError):
            FcmToken(**data)
