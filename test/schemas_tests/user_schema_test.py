import unittest
from datetime import date
from typing import List

from pydantic import ValidationError

from app.schemas.users import User, UserBase, UserCreate, UserLogin, UserUpdate


class TestUserBase(unittest.TestCase):

    def test_valid_instance(self):
        data = {
            "username": "username",
            "email": "username@example.com",
            "birth_date": date(1999, 10, 31),
            "city": "CABA",
            "preferences": ["Museum", "Cafe"],
        }

        user = UserBase(**data)

        self.assertEqual(user.username, "username")
        self.assertEqual(user.email, "username@example.com")
        self.assertEqual(user.birth_date, date(1999, 10, 31))
        self.assertEqual(user.city, "CABA")
        self.assertEqual(user.preferences, ["Museum", "Cafe"])

    def test_optional_fields(self):
        data = {"username": "username", "preferences": ["Cafe"]}

        user = UserBase(**data)

        self.assertEqual(user.username, "username")
        self.assertIsNone(user.email)
        self.assertIsNone(user.birth_date)
        self.assertIsNone(user.city)
        self.assertEqual(user.preferences, ["Cafe"])

    def test_default_preferences(self):
        user = UserBase(username="username", email="username@example.com")
        self.assertEqual(user.preferences, [])

    def test_invalid_email(self):
        data = {
            "username": "username",
            "email": "invalid_email",
        }

        with self.assertRaises(ValidationError):
            UserBase(**data)


class TestUserLogin(unittest.TestCase):

    def test_valid_user_login(self):
        data = {"email": "username@example.com", "password": "password"}

        user = UserLogin(**data)

        self.assertEqual(user.email, "username@example.com")
        self.assertEqual(user.password, "password")

    def test_invalid_password_length(self):
        data = {"email": "username@example.com", "password": "short"}

        with self.assertRaises(ValidationError):
            UserLogin(**data)


class TestUserUpdate(unittest.TestCase):

    def test_valid_user_update(self):
        data = {
            "username": "username",
            "email": "username@example.com",
            "birth_date": date(1999, 10, 31),
            "city": "Buenos Aires",
            "preferences": ["Cafe", "Aquarium"],
            "refresh_token": "refresh_token",
            "avatar_link": "avatar.jpg",
        }

        user = UserUpdate(**data)

        self.assertEqual(user.username, "username")
        self.assertEqual(user.email, "username@example.com")
        self.assertEqual(user.birth_date, date(1999, 10, 31))
        self.assertEqual(user.city, "Buenos Aires")
        self.assertEqual(user.preferences, ["Cafe", "Aquarium"])
        self.assertEqual(user.refresh_token, "refresh_token")
        self.assertEqual(user.avatar_link, "avatar.jpg")

    def test_invalid_avatar_link(self):
        data = {
            "username": "username",
            "email": "username@example.com",
            "avatar_link": 12345,  # Invalid link
        }

        with self.assertRaises(ValidationError):
            UserUpdate(**data)


class TestUserCreate(unittest.TestCase):

    def test_valid_user_create(self):
        data = {
            "username": "username",
            "email": "username@example.com",
            "birth_date": date(1999, 10, 31),
            "city": "Mendoza",
            "preferences": ["Library"],
            "password": "password",
            "fcm_token": "valid_fcm_token",
        }

        user = UserCreate(**data)

        self.assertEqual(user.username, "username")
        self.assertEqual(user.email, "username@example.com")
        self.assertEqual(user.birth_date, date(1999, 10, 31))
        self.assertEqual(user.city, "Mendoza")
        self.assertEqual(user.preferences, ["Library"])
        self.assertEqual(user.password, "password")
        self.assertEqual(user.fcm_token, "valid_fcm_token")

    def test_invalid_password_length(self):
        data = {
            "username": "username",
            "email": "username@example.com",
            "password": "short",
        }

        with self.assertRaises(ValidationError):
            UserCreate(**data)


class TestUser(unittest.TestCase):

    def test_valid_user(self):
        data = {
            "id": 1,
            "username": "username",
            "email": "username@example.com",
            "birth_date": date(1999, 10, 31),
            "city": "CABA",
            "preferences": ["Cafe"],
            "avatar_link": "avatar.jpg",
        }

        user = User(**data)

        self.assertEqual(user.id, 1)
        self.assertEqual(user.username, "username")
        self.assertEqual(user.email, "username@example.com")
        self.assertEqual(user.birth_date, date(1999, 10, 31))
        self.assertEqual(user.city, "CABA")
        self.assertEqual(user.preferences, ["Cafe"])
        self.assertEqual(user.avatar_link, "avatar.jpg")
