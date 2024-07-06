from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

import app
from app.main import app as app_routers
from app.services.password_services import *
from app.utils.api_exception import (
    INVALID_HEADER_ERROR,
    USER_DOES_NOT_EXISTS_ERROR,
    WRONG_PASSWORD_ERROR,
)
from app.utils.constants import *

client = TestClient(app_routers)


class TestPasswordRoutes:

    @patch("app.services.password_services.init_recover_password")
    def test_init_recover_password_success(self, mock_init_recover_password):
        mock_recover = {
            "user_id": 1,
            "email": "username@example.com",
            "code": "12das21",
            "emited_datetime": datetime.now().isoformat(),
            "leftover_attempts": 3,
        }
        mock_init_recover_password.return_value = mock_recover

        email = "username@example.com"
        response = client.post("/users/password/recover", json={"email": email})

        assert response.status_code == 200

    @patch("app.services.password_services.init_recover_password")
    def test_init_recover_password_user_not_exits(self, mock_init_recover_password):
        mock_init_recover_password.side_effect = APIException(
            code=USER_DOES_NOT_EXISTS_ERROR, msg="USER_DOES_NOT_EXISTS_ERROR"
        )

        email = "username@example.com"
        response = client.post("/users/password/recover", json={"email": email})

        assert response.status_code == 404

    @patch("app.services.password_services.recover_password")
    def test_recover_password_success(self, mock_recover_password):
        mock_recover_password.return_value = 1

        recover_data = {
            "email": "username@example.com",
            "code": "12das21",
            "new_password": "new_password",
        }

        response = client.put("/users/password/recover", json=recover_data)

        assert response.status_code == 200

    @patch("app.services.password_services.recover_password")
    def test_recover_password_user_not_found(self, mock_recover_password):
        mock_recover_password.side_effect = APIException(
            code=USER_DOES_NOT_EXISTS_ERROR, msg="USER_DOES_NOT_EXISTS_ERROR"
        )

        recover_data = {
            "email": "user_not_exist@example.com",
            "code": "12das21",
            "new_password": "new_password",
        }

        response = client.put("/users/password/recover", json=recover_data)

        assert response.status_code == 404

    @patch("app.services.password_services.update_password")
    def test_update_password_success(self, mock_update_password):
        mock_update_password.return_value = 1

        update_data = {
            "current_password": "current_password",
            "new_password": "new_password",
        }

        response = client.patch(
            "/users/password/update",
            json=update_data,
            headers={"Authorization": "Bearer token"},
        )

        assert response.status_code == 200

    @patch("app.services.password_services.update_password")
    def test_update_password_invalid_current_password(self, mock_update_password):
        mock_update_password.side_effect = APIException(
            code=WRONG_PASSWORD_ERROR, msg="Invalid current password"
        )

        update_data = {
            "current_password": "wrong_password",
            "new_password": "new_password",
        }

        response = client.patch(
            "/users/password/update",
            json=update_data,
            headers={"Authorization": "Bearer token"},
        )

        assert response.status_code == 400

    @patch("app.services.password_services.update_password")
    def test_update_password_user_not_authenticated(self, mock_update_password):
        mock_update_password.side_effect = APIException(
            code=INVALID_HEADER_ERROR, msg="Not authenticated"
        )

        update_data = {
            "current_password": "current_password",
            "new_password": "new_password",
        }

        response = client.patch(
            "/users/password/update",
            json=update_data,
            headers={"Authorization": "Bearer invalid_token"},
        )

        assert response.status_code == 403
