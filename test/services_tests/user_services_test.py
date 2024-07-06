import unittest
from unittest.mock import Mock, patch

import app
from app.auth.authentication import *
from app.auth.password import *
from app.db.user_crud import *
from app.schemas.chat import *
from app.schemas.token import *
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

    @patch("app.db.user_crud.get_user")
    def test_get_user_not_found(self, mock_get_user):
        mock_db = Mock(spec=Session)
        user_id = 1
        mock_get_user.return_value = None

        with self.assertRaises(APIException) as context:
            app.services.users_services.get_user(mock_db, user_id)

        self.assertEqual(context.exception.code, USER_DOES_NOT_EXISTS_ERROR)


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
            "fcm_token": "valid_fcm_token",
        }
        user_create_obj = UserCreate(**user_data)

        mock_get_user_by_email.return_value = None
        mock_create_user.return_value = User(id=1, **user_data)

        user = app.services.users_services.new_user(mock_db, user_create_obj)

        self.assertEqual(user.id, 1)

    @patch("app.db.user_crud.get_user_by_email")
    def test_new_user_email_exists(self, mock_get_user_by_email):
        mock_db = Mock(spec=Session)
        user_data = {
            "email": "username@example.com",
            "password": "password",
            "city": "Rosario",
            "preferences": ["Cafe", "Art"],
            "fcm_token": "valid_fcm_token",
        }
        user_create_obj = UserCreate(**user_data)

        mock_get_user_by_email.return_value = User(id=1, **user_data)

        with self.assertRaises(APIException) as context:
            app.services.users_services.new_user(mock_db, user_create_obj)

        self.assertEqual(context.exception.code, USER_EXISTS_ERROR)


class TestLogin(unittest.TestCase):
    @patch("app.services.users_services.create_session_tokens")
    @patch("app.auth.password.authenticate_user")
    def test_new_login_success(
        self, mock_authenticate_user, mock_create_session_tokens
    ):
        mock_db = Mock(spec=Session)
        user_login = UserLogin(email="username@example.com", password="password")
        db_user = Mock(spec=User)

        mock_authenticate_user.return_value = db_user
        mock_create_session_tokens.return_value = Token(
            token="access_token", refresh_token="refresh_token", token_type="bearer"
        )

        result = new_login(mock_db, user_login)

        self.assertEqual(result.token, "access_token")
        self.assertEqual(result.refresh_token, "refresh_token")
        self.assertEqual(result.token_type, "bearer")

    @patch("app.auth.password.authenticate_user")
    def test_new_login_invalid_credentials(self, mock_authenticate_user):
        mock_db = Mock(spec=Session)
        user_login = UserLogin(email="username@example.com", password="wrong_password")

        mock_authenticate_user.return_value = None

        with self.assertRaises(APIException) as context:
            new_login(mock_db, user_login)

        self.assertEqual(context.exception.code, LOGIN_ERROR)


class TestUserChat(unittest.TestCase):

    @patch("app.db.user_crud.update_user_chat")
    @patch("app.services.users_services.exception_handler")
    def test_new_chat_ids_success(self, mock_exception_handler, mock_update_user_chat):
        mock_db = Mock(spec=Session)
        chat = Chat(user_id=1, thread_id="thread_id", assistant_id="assistant_id")
        db_user = Mock(spec=User)

        mock_update_user_chat.return_value = db_user
        mock_exception_handler.return_value = db_user

        result = app.services.users_services.new_chat_ids(mock_db, chat)

        self.assertEqual(result, db_user)

    @patch("app.db.user_crud.get_user_chat")
    @patch("app.services.users_services.exception_handler")
    def test_get_user_chat_success(self, mock_exception_handler, mock_get_user_chat):
        mock_db = Mock(spec=Session)
        user_id = 1
        db_chat = Chat(
            user_id=user_id, thread_id="thread_id", assistant_id="assistant_id"
        )

        mock_get_user_chat.return_value = db_chat
        mock_exception_handler.return_value = db_chat

        result = app.services.users_services.get_user_chat(mock_db, user_id)

        self.assertEqual(result, db_chat)


class TestGetUserPreferences(unittest.TestCase):

    @patch("app.db.user_crud.get_user_preferences")
    def test_get_user_preferences_success(self, mock_get_user_preferences):
        mock_db = Mock(spec=Session)
        user_id = 1
        preferences = ["Cafe", "Museum"]

        mock_get_user_preferences.return_value = preferences

        result = app.services.users_services.get_user_preferences(mock_db, user_id)

        self.assertEqual(result, preferences)

    @patch("app.db.user_crud.get_user_preferences")
    def test_get_user_preferences_empty(self, mock_get_user_preferences):
        mock_db = Mock(spec=Session)
        user_id = 1

        mock_get_user_preferences.return_value = []

        result = app.services.users_services.get_user_preferences(mock_db, user_id)

        self.assertEqual(result, [])

    @patch("app.db.user_crud.get_user_preferences")
    def test_get_user_preferences_none(self, mock_get_user_preferences):
        mock_db = Mock(spec=Session)
        user_id = 1

        mock_get_user_preferences.return_value = None

        result = app.services.users_services.get_user_preferences(mock_db, user_id)

        self.assertEqual(result, [])

    @patch("app.db.user_crud.get_user_preferences")
    def test_get_user_preferences_exception(self, mock_get_user_preferences):
        mock_db = Mock(spec=Session)
        user_id = 1

        mock_get_user_preferences.side_effect = []

        with self.assertRaises(APIException):
            app.services.users_services.get_user_preferences(mock_db, user_id)


class TestUpdateAvatar(unittest.TestCase):

    @patch("app.services.users_services.auth.get_current_user")
    @patch("app.ext.firebase.upload_image")
    @patch("app.db.user_crud.update_user")
    def test_update_avatar_success(
        self, mock_update_user, mock_upload_image, mock_get_current_user
    ):
        mock_db = Mock(spec=Session)
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="valid_token"
        )
        avatar = Mock(spec=UploadFile)
        avatar.content_type = "image/png"
        avatar.filename = "avatar.png"
        avatar.file = Mock()

        mock_get_current_user.return_value = 1
        mock_upload_image.return_value = "http://image.url/avatar.png"
        mock_update_user.return_value = Mock(spec=User)

        result = app.services.users_services.update_avatar(mock_db, credentials, avatar)

        self.assertIsInstance(result, User)

    @patch("app.services.users_services.auth.get_current_user")
    def test_update_avatar_invalid_scheme(self, mock_get_current_user):
        mock_db = Mock(spec=Session)
        credentials = HTTPAuthorizationCredentials(
            scheme="Basic", credentials="valid_token"
        )
        avatar = Mock(spec=UploadFile)

        with self.assertRaises(APIException) as context:
            app.services.users_services.update_avatar(mock_db, credentials, avatar)

        self.assertEqual(context.exception.code, INVALID_HEADER_ERROR)

    @patch("app.services.users_services.auth.get_current_user")
    @patch("app.ext.firebase.upload_image")
    def test_update_avatar_get_current_user_failure(
        self, mock_upload_image, mock_get_current_user
    ):
        mock_db = Mock(spec=Session)
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="invalid_token"
        )
        avatar = Mock(spec=UploadFile)

        mock_get_current_user.side_effect = APIException(
            code=USER_DOES_NOT_EXISTS_ERROR, msg="USER_DOES_NOT_EXISTS_ERROR"
        )

        with self.assertRaises(APIException) as context:
            app.services.users_services.update_avatar(mock_db, credentials, avatar)

        self.assertEqual(context.exception.code, USER_DOES_NOT_EXISTS_ERROR)


class TestFcmToken(unittest.TestCase):

    @patch("app.db.user_crud.get_user_fcm_token")
    def test_get_fcm_token_success(self, mock_get_user_fcm_token):
        mock_db = Mock(spec=Session)
        user_id = 1
        fcm_token = "fcm_token_example"

        mock_get_user_fcm_token.return_value = fcm_token

        result = app.services.users_services.get_fcm_token(mock_db, user_id)

        self.assertEqual(result, fcm_token)

    @patch("app.db.user_crud.get_user_fcm_token")
    def test_get_fcm_token_user_not_exists(self, mock_get_user_fcm_token):
        mock_db = Mock(spec=Session)
        user_id = 1

        mock_get_user_fcm_token.return_value = None

        with self.assertRaises(APIException) as context:
            app.services.users_services.get_fcm_token(mock_db, user_id)

        self.assertEqual(context.exception.code, USER_DOES_NOT_EXISTS_ERROR)

    @patch("app.db.user_crud.update_user_fcm_token")
    def test_update_fcm_token_success(self, mock_update_user_fcm_token):
        mock_db = Mock(spec=Session)
        user_id = 1
        token = "new_fcm_token"
        mock_user = Mock(spec=User)

        mock_update_user_fcm_token.return_value = mock_user

        result = app.services.users_services.update_fcm_token(mock_db, user_id, token)

        self.assertEqual(result, mock_user)

    @patch("app.db.user_crud.update_user_fcm_token")
    def test_update_fcm_token_user_not_exists(self, mock_update_user_fcm_token):
        mock_db = Mock(spec=Session)
        user_id = 1
        token = "new_fcm_token"

        mock_update_user_fcm_token.return_value = None

        with self.assertRaises(APIException) as context:
            app.services.users_services.update_fcm_token(mock_db, user_id, token)

        self.assertEqual(context.exception.code, USER_DOES_NOT_EXISTS_ERROR)
