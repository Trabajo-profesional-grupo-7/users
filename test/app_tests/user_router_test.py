from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

import app
from app.main import app as user_router
from app.schemas.users import *
from app.services.users_services import *
from app.utils.api_exception import *
from app.utils.constants import *

client = TestClient(user_router)


class TestUserRoutes:

    @patch("app.services.users_services.update_user")
    def test_update_user_profile_success(self, mock_update_user):
        mock_user = User(id=1, username="username", email="username@example.com")
        mock_update_user.return_value = mock_user

        updated_data = {"username": "username", "email": "username@example.com"}
        response = client.patch(
            "/users", json=updated_data, headers={"Authorization": "Bearer token"}
        )

        assert response.status_code == 200

    @patch("app.services.users_services.update_user")
    def test_update_user_profile_user_not_authenticated(self, mock_update_user):
        mock_update_user.side_effect = APIException(
            code=INVALID_HEADER_ERROR, msg="Not authenticated"
        )

        updated_data = {"username": "username", "email": "username@example.com"}
        response = client.patch("/users", json=updated_data)

        assert response.status_code == 403

    @patch("app.services.users_services.delete_user")
    def test_delete_user_profile_success(self, mock_delete_user):
        mock_user = User(id=1, username="username", email="username@example.com")
        mock_delete_user.return_value = mock_user
        response = client.delete("/users", headers={"Authorization": "Bearer token"})

        assert response.status_code == 200

    @patch("app.services.users_services.delete_user")
    def test_delete_user_profile_user_not_authenticated(self, mock_delete_user):
        mock_delete_user.side_effect = APIException(
            code=INVALID_HEADER_ERROR, msg="Not authenticated"
        )

        response = client.delete("/users")

        assert response.status_code == 403

    @patch("app.services.users_services.get_user")
    def test_get_user_profile_success(self, mock_get_user):
        mock_user = User(id=1, username="username", email="username@example.com")
        mock_get_user.return_value = mock_user

        response = client.get("/users/1")

        assert response.status_code == 200

    @patch("app.services.users_services.get_user")
    def test_get_user_profile_user_not_found(self, mock_get_user):
        mock_get_user.side_effect = APIException(
            code=USER_DOES_NOT_EXISTS_ERROR, msg="USER_DOES_NOT_EXISTS_ERROR"
        )

        response = client.get("/users/2")

        assert response.status_code == 404

    @patch("app.services.users_services.get_user")
    def test_get_user_profile_invalid_id(self, mock_get_user):
        response = client.get("/users/invalid_id")

        assert response.status_code == 422

    @patch("app.services.users_services.new_chat_ids")
    def test_new_chat_success(self, mock_new_chat_ids):
        mock_user = User(id=1, username="username", email="username@example.com")
        mock_new_chat_ids.return_value = mock_user

        chat_data = {
            "user_id": 1,
            "thread_id": "thread_id",
            "assistant_id": "assistant_id",
        }

        response = client.post("/users/chat", json=chat_data)

        assert response.status_code == 200

    @patch("app.services.users_services.new_chat_ids")
    def test_new_chat_user_not_found(self, mock_new_chat_ids):
        mock_new_chat_ids.side_effect = APIException(
            code=USER_DOES_NOT_EXISTS_ERROR, msg="USER_DOES_NOT_EXISTS_ERROR"
        )

        chat_data = {
            "user_id": 1,
            "thread_id": "thread_id",
            "assistant_id": "assistant_id",
        }

        response = client.post("/users/chat", json=chat_data)

        assert response.status_code == 404

    @patch("app.services.users_services.get_user_chat")
    def test_get_user_chat_success(self, mock_get_user_chat):
        mock_chat = Chat(
            user_id=1,
            thread_id="thread_id",
            assistant_id="assistant_id",
        )
        mock_get_user_chat.return_value = mock_chat

        response = client.get(f"/users/{mock_chat.user_id}/chat")

        assert response.status_code == 200

    @patch("app.services.users_services.get_user_chat")
    def test_get_user_chat_user_not_exists(self, mock_get_user_chat):
        mock_get_user_chat.side_effect = APIException(
            code=USER_DOES_NOT_EXISTS_ERROR, msg="USER_DOES_NOT_EXISTS_ERROR"
        )

        user_id = 1

        response = client.get(f"/users/{user_id}/chat")

        assert response.status_code == 404

    @patch("app.services.users_services.get_user_preferences")
    def test_get_user_preferences_success(self, mock_get_user_preferences):
        mock_preferences = ["Museum", "Park", "Cafe"]
        mock_get_user_preferences.return_value = mock_preferences

        user_id = 1
        response = client.get(f"/users/{user_id}/preferences")

        assert response.status_code == 200

    @patch("app.services.users_services.get_user_preferences")
    def test_get_user_preferences_user_not_exists(self, mock_get_user_preferences):
        mock_get_user_preferences.side_effect = APIException(
            code=USER_DOES_NOT_EXISTS_ERROR, msg="USER_DOES_NOT_EXISTS_ERROR"
        )

        user_id = 1
        response = client.get(f"/users/{user_id}/preferences")

        assert response.status_code == 404

    @patch("app.services.users_services.update_fcm_token")
    def test_update_fcm_token_user_not_found(self, mock_update_fcm_token):
        mock_user_id = 0000
        mock_update_fcm_token.side_effect = APIException(
            code=USER_DOES_NOT_EXISTS_ERROR, msg=f"USER_DOES_NOT_EXISTS_ERROR"
        )

        fcm_token_data = {"user_id": mock_user_id, "fcm_token": "mock_fcm_token"}

        response = client.post("/users/fcm_token", json=fcm_token_data)

        assert response.status_code == 404

    @patch("app.services.users_services.get_fcm_token")
    def test_get_fcm_token_success(self, mock_get_fcm_token):
        mock_user_id = 1
        mock_fcm_token = "mock_fcm_token"
        mock_get_fcm_token.return_value = mock_fcm_token

        response = client.get(f"/users/{mock_user_id}/fcm_token")

        assert response.status_code == 200

    @patch("app.services.users_services.get_fcm_token")
    def test_get_fcm_token_user_not_found(self, mock_get_fcm_token):
        mock_user_id = 0000
        mock_get_fcm_token.side_effect = APIException(
            code=USER_DOES_NOT_EXISTS_ERROR, msg=f"USER_DOES_NOT_EXISTS_ERROR"
        )

        response = client.get(f"/users/{mock_user_id}/fcm_token")

        assert response.status_code == 404
