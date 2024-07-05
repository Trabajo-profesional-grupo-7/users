import unittest
from unittest.mock import Mock, call, patch

import app
from app.auth.authentication import *
from app.auth.password import *
from app.db.user_crud import *
from app.schemas.users import *
from app.services.password_services import *
from app.services.users_services import *
from app.utils.api_exception import *
from app.utils.constants import *


class TestGetUser(unittest.TestCase):

    @patch("app.db.user_crud.get_user")
    def test_get_user(self, mock_get_user):
        mock_db = Mock(spec=Session)
        user_id = 1
        mock_get_user.return_value = User(id=user_id, username="username")

        user = app.services.users_services.get_user(mock_db, user_id)

        self.assertEqual(user.id, user_id)
        self.assertEqual(user.username, "username")
        mock_get_user.assert_called_once_with(mock_db, user_id)

    @patch("app.db.user_crud.get_user")
    def test_get_user_not_found(self, mock_get_user):
        mock_db = Mock(spec=Session)
        user_id = 1
        mock_get_user.return_value = None

        with self.assertRaises(APIException) as context:
            app.services.users_services.get_user(mock_db, user_id)

        self.assertEqual(context.exception.code, USER_DOES_NOT_EXISTS_ERROR)
        mock_get_user.assert_called_once_with(mock_db, user_id)


class TestDeleteUser(unittest.TestCase):

    @patch("app.auth.authentication.get_current_user")
    @patch("app.db.user_crud.delete_user")
    def test_delete_user(self, mock_delete_user, mock_get_current_user):
        mock_db = Mock(spec=Session)
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="valid_token"
        )

        mock_get_current_user.return_value = 1
        mock_delete_user.return_value = User(id=1, username="username")

        user = app.services.users_services.delete_user(mock_db, credentials)

        self.assertEqual(user.id, 1)
        self.assertEqual(user.username, "username")
        mock_delete_user.assert_called_once_with(mock_db, 1)

    @patch("app.auth.authentication.get_current_user")
    @patch("app.db.user_crud.delete_user")
    def test_delete_user_not_authenticated(
        self, mock_delete_user, mock_get_current_user
    ):
        mock_db = Mock(spec=Session)
        credentials = HTTPAuthorizationCredentials(
            scheme="Basic", credentials="invalid_token"
        )

        mock_get_current_user.return_value = None

        with self.assertRaises(APIException) as context:
            app.services.users_services.delete_user(mock_db, credentials)

        self.assertEqual(context.exception.code, INVALID_HEADER_ERROR)
        mock_delete_user.assert_not_called()

    @patch("app.auth.authentication.get_current_user")
    @patch("app.db.user_crud.delete_user")
    def test_delete_user_user_not_exists(self, mock_delete_user, mock_get_current_user):
        mock_db = Mock(spec=Session)
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="valid_token"
        )

        mock_get_current_user.return_value = 1
        mock_delete_user.return_value = None

        with self.assertRaises(APIException) as context:
            app.services.users_services.delete_user(mock_db, credentials)

        self.assertEqual(context.exception.code, USER_DOES_NOT_EXISTS_ERROR)
        mock_delete_user.assert_called_once_with(mock_db, 1)


class TestUpdateUser(unittest.TestCase):

    @patch("app.auth.authentication.get_current_user")
    @patch("app.db.user_crud.update_user")
    @patch("app.services.users_services.update_recommendations")
    def test_update_user_success(
        self, mock_update_recommendations, mock_update_user, mock_get_current_user
    ):
        mock_db = Mock(spec=Session)
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="valid_token"
        )
        updated_user_data = UserBase(preferences=["Nigth club"], city="Buenos Aires")
        mock_updated_user = Mock(spec=User)
        mock_updated_user.preferences = [
            "Museum",
            "Cafe",
        ]
        mock_updated_user.city = "Buenos Aires"

        mock_get_current_user.return_value = 1
        mock_update_user.return_value = mock_updated_user

        user = app.services.users_services.update_user(
            mock_db, credentials, updated_user_data
        )

        self.assertEqual(user.preferences, mock_updated_user.preferences)
        self.assertEqual(user.city, mock_updated_user.city)
        mock_update_user.assert_called_once_with(mock_db, 1, updated_user_data)
        mock_update_recommendations.assert_called_once_with(
            1, "Buenos Aires", ["Museum", "Cafe"]
        )

    def test_update_user_invalid_scheme(self):
        mock_db = Mock(spec=Session)
        credentials = HTTPAuthorizationCredentials(
            scheme="Basic", credentials="invalid_token"
        )
        updated_user_data = UserBase(preferences=["Cafe"], city="Buenos Aires")

        with self.assertRaises(APIException) as context:
            app.services.users_services.update_user(
                mock_db, credentials, updated_user_data
            )

        self.assertEqual(context.exception.code, INVALID_HEADER_ERROR)

    @patch("app.auth.authentication.get_current_user")
    @patch("app.db.user_crud.update_user")
    def test_update_user_user_not_exists(self, mock_update_user, mock_get_current_user):
        mock_db = Mock(spec=Session)
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="valid_token"
        )
        updated_user_data = UserBase(preferences=["Aquarium"], city="Buenos Aires")

        mock_get_current_user.return_value = 1
        mock_update_user.return_value = None

        with self.assertRaises(APIException) as context:
            app.services.users_services.update_user(
                mock_db, credentials, updated_user_data
            )

        self.assertEqual(context.exception.code, USER_DOES_NOT_EXISTS_ERROR)


class TestNewUser(unittest.TestCase):

    @patch("app.db.user_crud.get_user_by_email")
    @patch("app.db.user_crud.create_user")
    @patch("app.services.users_services.update_recommendations")
    @patch("app.services.users_services.create_assistant")
    def test_new_user_success(
        self,
        mock_create_assistant,
        mock_update_recommendations,
        mock_create_user,
        mock_get_user_by_email,
    ):
        mock_db = Mock(spec=Session)
        user_data = {
            "email": "username@example.com",
            "password": "password",
            "city": "Buenos Aires",
            "preferences": ["Cafe", "Library"],
        }
        user_create_obj = UserCreate(**user_data)

        mock_get_user_by_email.return_value = None
        mock_create_user.return_value = User(id=1, **user_data)

        user = app.services.users_services.new_user(mock_db, user_create_obj)

        self.assertEqual(user.id, 1)
        mock_get_user_by_email.assert_called_once_with(
            mock_db, email=user_data["email"]
        )
        mock_create_user.assert_called_once_with(db=mock_db, user=user_create_obj)
        mock_update_recommendations.assert_called_once_with(
            1, "Buenos Aires", ["Cafe", "Library"]
        )
        mock_create_assistant.assert_called_once_with(1)

    @patch("app.db.user_crud.get_user_by_email")
    def test_new_user_email_exists(self, mock_get_user_by_email):
        mock_db = Mock(spec=Session)
        user_data = {
            "email": "username@example.com",
            "password": "password",
            "city": "Rosario",
            "preferences": ["Cafe", "Art"],
        }
        user_create_obj = UserCreate(**user_data)

        mock_get_user_by_email.return_value = User(id=1, **user_data)

        with self.assertRaises(APIException) as context:
            app.services.users_services.new_user(mock_db, user_create_obj)

        self.assertEqual(context.exception.code, USER_EXISTS_ERROR)
        mock_get_user_by_email.assert_called_once_with(
            mock_db, email=user_data["email"]
        )
