import unittest
from unittest.mock import patch

from fastapi.exceptions import HTTPException
from fastapi.testclient import TestClient

import app
from app.main import app as routers
from app.schemas.password import *
from app.schemas.token import *
from app.schemas.users import *
from app.services.users_services import *
from app.utils.api_exception import (
    EXPIRED_TOKEN_ERROR,
    INVALID_HEADER_ERROR,
    LOGIN_ERROR,
)
from app.utils.constants import *

client = TestClient(routers)


class TestAuthRoutes(unittest.TestCase):

    @patch("app.routes.auth_router.srv.new_user")
    def test_create_user(self, mock_new_user):
        mock_new_user.return_value = User(
            id=1,
            username="username",
            email="username@mail.com",
            creation_date="2021-01-01",
            blocked=False,
        )
        response = client.post(
            "/users/signup",
            json={
                "username": "username",
                "email": "username@mail.com",
                "password": "password",
                "password_confirmation": "password",
                "fcm_token": "valid_fcm_token",
            },
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["username"], "username")

    @patch("app.routes.auth_router.srv.new_user")
    def test_create_user_failure(self, mock_new_user):
        mock_new_user.side_effect = HTTPException(
            status_code=422, detail="Validation Error"
        )

        response = client.post(
            "/users/signup",
            json={
                "username": "username",
                "email": "username@mail.com",
                "password": "password",
                "password_confirmation": "password",
                "fcm_token": "your_fcm_token_here",
            },
        )

        self.assertEqual(response.status_code, 422)
        self.assertIn("Validation Error", response.text)

    @patch("app.services.users_services.new_login")
    def test_login_user_success(self, mock_new_login):
        mock_new_login.return_value = {
            "token": "access_token",
            "refresh_token": "refresh_token",
            "token_type": "bearer",
        }

        response = client.post(
            "/users/login", json={"username": "username", "password": "password"}
        )

        assert response.status_code == 200

    @patch("app.services.users_services.new_login")
    def test_login_user_invalid_credentials(self, mock_new_login):
        mock_new_login.side_effect = APIException(
            code=LOGIN_ERROR, msg=f"Invalid credentials"
        )

        response = client.post(
            "/users/login", json={"username": "username", "password": "wrong_password"}
        )

        assert response.status_code == 400

    @patch("app.services.users_services.auth_user")
    def test_verify_id_token_success(self, mock_auth_user):
        mock_auth_user.return_value = 1

        token = "jwt_token"
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/users/verify_id_token", headers=headers)

        assert response.status_code == 200

    @patch("app.services.users_services.auth_user")
    def test_verify_id_token_unauthorized(self, mock_auth_user):
        mock_auth_user.side_effect = APIException(
            code=INVALID_HEADER_ERROR, msg="INVALID_HEADER_ERROR"
        )

        response = client.get("/users/verify_id_token")

        assert response.status_code == 403

    @patch("app.services.users_services.refresh_user_tokens")
    def test_refresh_token_success(self, mock_refresh_user_tokens):
        mock_tokens = {
            "token": "access_token",
            "refresh_token": "refresh_token",
            "token_type": "bearer",
        }
        mock_refresh_user_tokens.return_value = mock_tokens

        token = "refresh_token"
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post("/users/refresh_token", headers=headers)

        assert response.status_code == 200

    @patch("app.services.users_services.refresh_user_tokens")
    def test_refresh_token_unauthorized(self, mock_refresh_user_tokens):
        mock_refresh_user_tokens.side_effect = APIException(
            code=INVALID_HEADER_ERROR, msg="INVALID_HEADER_ERROR"
        )

        response = client.post("/users/refresh_token")

        assert response.status_code == 403
