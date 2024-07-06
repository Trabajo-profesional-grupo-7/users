import unittest
from unittest.mock import Mock, call, patch

import app
from app.auth.authentication import *
from app.auth.password import *
from app.schemas.password import *
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

    @patch("app.auth.authentication.authorize_token")
    def test_auth_user_success(self, mock_authorize_token):
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="valid_token"
        )
        mock_authorize_token.return_value = 1

        result = app.services.users_services.auth_user(credentials)

        self.assertEqual(result, 1)

    def test_auth_user_invalid_scheme(self):
        credentials = HTTPAuthorizationCredentials(
            scheme="Basic", credentials="invalid_token"
        )

        with self.assertRaises(APIException) as context:
            app.services.users_services.auth_user(credentials)

        self.assertEqual(context.exception.code, INVALID_HEADER_ERROR)

    def test_refresh_user_tokens_invalid_scheme(self):
        mock_db = Mock(spec=Session)
        credentials = HTTPAuthorizationCredentials(
            scheme="Basic", credentials="invalid_refresh_token"
        )

        with self.assertRaises(APIException) as context:
            app.services.users_services.refresh_user_tokens(mock_db, credentials)

        self.assertEqual(context.exception.code, INVALID_HEADER_ERROR)

    @patch("app.auth.authentication.get_current_user")
    @patch("app.db.user_crud.get_user")
    def test_refresh_user_tokens_invalid_refresh_token(
        self, mock_get_user, mock_get_current_user
    ):
        mock_db = Mock(spec=Session)
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="invalid_refresh_token"
        )
        mock_get_current_user.return_value = 1
        mock_get_user.return_value = Mock(refresh_token="valid_refresh_token")

        with self.assertRaises(APIException) as context:
            app.services.users_services.refresh_user_tokens(mock_db, credentials)

        self.assertEqual(context.exception.code, INVALID_CREDENTIALS_ERROR)


class TestRecoverPassword(unittest.TestCase):

    @patch("app.db.user_crud.get_user_by_email")
    @patch("app.db.pwd_recover_crud.get_recover")
    @patch("app.db.pwd_recover_crud.delete_recover")
    @patch("app.db.pwd_recover_crud.new_pwd_recover")
    @patch("app.services.password_services.send_email")
    def test_init_recover_password_user_not_exist(
        self,
        mock_send_email,
        mock_new_pwd_recover,
        mock_delete_recover,
        mock_get_recover,
        mock_get_user_by_email,
    ):
        mock_db = Mock()
        mock_get_user_by_email.return_value = None

        with self.assertRaises(APIException) as context:
            app.services.password_services.init_recover_password(
                mock_db, "username@example.com"
            )

        self.assertEqual(context.exception.code, USER_DOES_NOT_EXISTS_ERROR)

    @patch("app.db.user_crud.get_user_by_email")
    @patch("app.db.pwd_recover_crud.get_recover")
    @patch("app.db.pwd_recover_crud.delete_recover")
    @patch("app.db.pwd_recover_crud.new_pwd_recover")
    @patch("app.services.password_services.send_email")
    @patch("app.services.password_services.random.randint")
    def test_init_recover_password_existing_recover(
        self,
        mock_randint,
        mock_send_email,
        mock_new_pwd_recover,
        mock_delete_recover,
        mock_get_recover,
        mock_get_user_by_email,
    ):
        mock_db = Mock()
        mock_user = Mock()
        mock_user.id = 1
        mock_get_user_by_email.return_value = mock_user
        mock_get_recover.return_value = Mock()

        mock_randint.return_value = 1226

        app.services.password_services.init_recover_password(
            mock_db, "username@example.com"
        )

        mock_new_pwd_recover.assert_called_once()

    @patch("app.db.user_crud.get_user_by_email")
    @patch("app.db.pwd_recover_crud.get_recover")
    @patch("app.db.pwd_recover_crud.delete_recover")
    @patch("app.db.pwd_recover_crud.new_pwd_recover")
    @patch("app.services.password_services.send_email")
    @patch("app.services.password_services.random.randint")
    def test_init_recover_password_success(
        self,
        mock_randint,
        mock_send_email,
        mock_new_pwd_recover,
        mock_delete_recover,
        mock_get_recover,
        mock_get_user_by_email,
    ):
        mock_db = Mock()
        mock_user = Mock()
        mock_user.id = 1
        mock_get_user_by_email.return_value = mock_user
        mock_get_recover.return_value = None

        mock_randint.return_value = 1234

        mock_new_pwd_recover.return_value = PasswordRecover(
            user_id=mock_user.id, emited_datetime=datetime.now(), leftover_attempts=5
        )

        result = init_recover_password(mock_db, "username@example.com")

        self.assertIsInstance(result, PasswordRecover)
        self.assertEqual(result.user_id, mock_user.id)
        self.assertEqual(result.leftover_attempts, 5)

    @patch("app.db.user_crud.get_user_by_email")
    @patch("app.db.pwd_recover_crud.get_recover")
    @patch("app.db.pwd_recover_crud.delete_recover")
    @patch("app.db.pwd_recover_crud.update_recover_attemps")
    @patch("app.services.password_services.update_password")
    @patch("app.auth.password.get_password_hash")
    def test_recover_password_success(
        self,
        mock_get_password_hash,
        mock_update_password,
        mock_update_recover_attempts,
        mock_delete_recover,
        mock_get_recover,
        mock_get_user_by_email,
    ):
        mock_db = Mock()
        mock_user = Mock()
        mock_user.id = 1
        mock_get_user_by_email.return_value = mock_user

        mock_recover_data = UpdateRecoverPassword(
            email="username@example.com", code="1234", new_password="new_password"
        )

        mock_db_recover = Mock()
        mock_db_recover.emited_datetime = datetime.now() - timedelta(minutes=20)
        mock_db_recover.pin = "1234"
        mock_db_recover.leftover_attempts = 2
        mock_get_recover.return_value = mock_db_recover

        mock_get_password_hash.return_value = "hashed_password"

        result = app.services.password_services.recover_password(
            mock_db, mock_recover_data
        )

        self.assertEqual(result, mock_user.id)

    @patch("app.db.user_crud.get_user_by_email")
    @patch("app.db.pwd_recover_crud.get_recover")
    @patch("app.db.pwd_recover_crud.delete_recover")
    def test_recover_password_user_not_exist(
        self, mock_delete_recover, mock_get_recover, mock_get_user_by_email
    ):
        mock_db = Mock()
        mock_get_user_by_email.return_value = None

        mock_recover_data = UpdateRecoverPassword(
            email="username_not_exist@example.com",
            code="1256",
            new_password="new_password",
        )

        with self.assertRaises(APIException) as context:
            app.services.password_services.recover_password(mock_db, mock_recover_data)

        self.assertEqual(context.exception.code, USER_DOES_NOT_EXISTS_ERROR)

    @patch("app.db.user_crud.get_user_by_email")
    @patch("app.db.pwd_recover_crud.get_recover")
    @patch("app.db.pwd_recover_crud.delete_recover")
    def test_recover_password_recovery_not_initiated(
        self, mock_delete_recover, mock_get_recover, mock_get_user_by_email
    ):
        mock_db = Mock()
        mock_user = Mock()
        mock_user.id = 1
        mock_get_user_by_email.return_value = mock_user
        mock_get_recover.return_value = None

        mock_recover_data = UpdateRecoverPassword(
            email="username@example.com", code="1234", new_password="new_password"
        )

        with self.assertRaises(APIException) as context:
            app.services.password_services.recover_password(mock_db, mock_recover_data)

        self.assertEqual(context.exception.code, RECOVERY_NOT_INITIATED_ERROR)

    @patch("app.db.user_crud.get_user_by_email")
    @patch("app.db.pwd_recover_crud.get_recover")
    @patch("app.db.pwd_recover_crud.delete_recover")
    @patch("app.db.pwd_recover_crud.update_recover_attemps")
    def test_recover_password_invalid_code_last_attempt(
        self,
        mock_update_recover_attempts,
        mock_delete_recover,
        mock_get_recover,
        mock_get_user_by_email,
    ):
        mock_db = Mock()
        mock_user = Mock()
        mock_user.id = 1
        mock_get_user_by_email.return_value = mock_user

        mock_db_recover = Mock()
        mock_db_recover.emited_datetime = datetime.now() - timedelta(minutes=20)
        mock_db_recover.pin = "1234"
        mock_db_recover.leftover_attempts = 0
        mock_get_recover.return_value = mock_db_recover

        mock_recover_data = UpdateRecoverPassword(
            email="username@example.com", code="12354", new_password="new_password"
        )

        with self.assertRaises(APIException) as context:
            app.services.password_services.recover_password(mock_db, mock_recover_data)

        self.assertEqual(context.exception.code, INVALID_RECOVERY_CODE_ERROR)
