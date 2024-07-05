import unittest
from unittest.mock import Mock, call, patch

import app
from app.auth.authentication import *
from app.auth.password import *
from app.schemas.users import *
from app.services.password_services import *
from app.services.users_services import *
from app.utils.api_exception import *
from app.utils.constants import *


class TestPassword(unittest.TestCase):

    @patch("app.auth.authentication.get_current_user")
    @patch("app.db.user_crud.get_user")
    @patch("app.auth.password.verify_password")
    @patch("app.auth.password.get_password_hash")
    @patch("app.services.users_services.update_password")
    def test_update_password(
        self,
        mock_update_password,
        mock_get_password_hash,
        mock_verify_password,
        mock_get_user,
        mock_get_current_user,
    ):
        mock_db = Mock(spec=Session)
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="valid token"
        )
        current_password = "current-password"
        new_password = "new-password"

        mock_get_current_user.return_value = 1
        mock_get_user.return_value = Mock(
            id=1, hashed_password="hashed-current-password"
        )
        mock_verify_password.return_value = True
        mock_get_password_hash.return_value = "hashed-new-password"
        mock_update_password.return_value = Mock(id=1)

        user = app.services.users_services.update_password(
            mock_db, credentials, current_password, new_password
        )

        self.assertEqual(user.id, 1)

    def test_update_password_invalid_user(self):
        mock_db = Mock(spec=Session)
        user_id = 104694
        new_password_hashed = "hashed-new-passwor"

        with patch(
            "app.db.user_crud.update_user_pwd",
            side_effect=APIException(
                code=USER_DOES_NOT_EXISTS_ERROR, msg="USER_DOES_NOT_EXIST"
            ),
        ):
            with self.assertRaises(APIException) as context:
                app.services.users_services.update_password(
                    mock_db, user_id, new_password_hashed
                )
            self.assertEqual(context.exception.code, USER_DOES_NOT_EXISTS_ERROR)


class TestToken(unittest.TestCase):

    @patch("app.auth.authentication.get_current_user")
    @patch("app.db.user_crud.get_user")
    @patch("app.services.users_services.create_session_tokens")
    def test_refresh_user_tokens_success(
        self, mock_create_session_tokens, mock_get_user, mock_get_current_user
    ):
        mock_db = Mock(spec=Session)
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="valid_refresh_token"
        )
        mock_user = Mock(spec=User, refresh_token="valid_refresh_token")
        mock_token = Mock(spec=Token)

        mock_get_current_user.return_value = 1
        mock_get_user.return_value = mock_user
        mock_create_session_tokens.return_value = mock_token

        token = app.services.users_services.refresh_user_tokens(mock_db, credentials)

        self.assertEqual(token, mock_token)
        mock_create_session_tokens.assert_called_once_with(mock_db, mock_user)

    def test_refresh_user_tokens_invalid_scheme(self):
        mock_db = Mock(spec=Session)
        credentials = HTTPAuthorizationCredentials(
            scheme="Basic", credentials="invalid_token"
        )

        with self.assertRaises(APIException) as context:
            app.services.users_services.refresh_user_tokens(mock_db, credentials)

        self.assertEqual(context.exception.code, INVALID_HEADER_ERROR)

    @patch("app.auth.authentication.get_current_user")
    @patch("app.db.user_crud.get_user")
    @patch("app.services.users_services.create_session_tokens")
    def test_refresh_user_tokens_invalid_refresh_token(
        self, mock_create_session_tokens, mock_get_user, mock_get_current_user
    ):
        mock_db = Mock(spec=Session)
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="invalid_refresh_token"
        )
        mock_user = Mock(spec=User, refresh_token="valid_refresh_token")

        mock_get_current_user.return_value = 1
        mock_get_user.return_value = mock_user

        with self.assertRaises(APIException) as context:
            app.services.users_services.refresh_user_tokens(mock_db, credentials)

        self.assertEqual(context.exception.code, INVALID_CREDENTIALS_ERROR)
