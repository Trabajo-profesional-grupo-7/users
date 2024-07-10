import unittest
from datetime import datetime

from pydantic import ValidationError

from app.schemas.password import (
    InitRecoverPassword,
    PasswordRecover,
    PasswordRecoverCreate,
    UpdatePassword,
    UpdateRecoverPassword,
)


class TestInitRecoverPassword(unittest.TestCase):

    def test_valid_password_recover(self):
        data = {"email": "username@example.com"}

        recover_password = InitRecoverPassword(**data)

        self.assertEqual(recover_password.email, "username@example.com")

    def test_invalid_email(self):
        data = {"email": "invalid-email"}

        with self.assertRaises(ValidationError):
            InitRecoverPassword(**data)


class TestUpdateRecoverPassword(unittest.TestCase):

    def test_valid_update_password_recover(self):
        data = {
            "email": "username@example.com",
            "code": "a4sd7s",
            "new_password": "valid_password",
        }

        update_recover_password = UpdateRecoverPassword(**data)

        self.assertEqual(update_recover_password.email, "username@example.com")
        self.assertEqual(update_recover_password.code, "a4sd7s")
        self.assertEqual(update_recover_password.new_password, "valid_password")

    def test_invalid_new_password_short(self):
        data = {
            "email": "username@example.com",
            "code": "fd34gd",
            "new_password": "short",
        }

        with self.assertRaises(ValidationError):
            UpdateRecoverPassword(**data)


class TestUpdatePassword(unittest.TestCase):

    def test_valid_update_password(self):
        data = {"current_password": "old_password", "new_password": "valid_password"}

        update_password = UpdatePassword(**data)

        self.assertEqual(update_password.current_password, "old_password")
        self.assertEqual(update_password.new_password, "valid_password")

    def test_invalid_new_password_short(self):
        data = {"current_password": "old_password", "new_password": "short"}

        with self.assertRaises(ValidationError):
            UpdatePassword(**data)


class TestPasswordRecover(unittest.TestCase):

    def test_valid_password_recover(self):
        data = {"user_id": 1, "emited_datetime": datetime.now(), "leftover_attempts": 3}

        password_recover = PasswordRecover(**data)

        self.assertEqual(password_recover.user_id, 1)
        self.assertEqual(password_recover.emited_datetime, data["emited_datetime"])
        self.assertEqual(password_recover.leftover_attempts, 3)


class TestPasswordRecoverCreate(unittest.TestCase):

    def test_valid_password_recover_create(self):
        data = {
            "user_id": 1,
            "emited_datetime": datetime.now(),
            "leftover_attempts": 3,
            "pin": "1d4f56",
        }

        password_recover_create = PasswordRecoverCreate(**data)

        self.assertEqual(password_recover_create.user_id, 1)
        self.assertEqual(
            password_recover_create.emited_datetime, data["emited_datetime"]
        )
        self.assertEqual(password_recover_create.leftover_attempts, 3)
        self.assertEqual(password_recover_create.pin, "1d4f56")
