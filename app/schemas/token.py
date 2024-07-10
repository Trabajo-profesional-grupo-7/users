from pydantic import BaseModel


class Token(BaseModel):
    token: str
    refresh_token: str
    token_type: str


class FcmToken(BaseModel):
    user_id: int
    fcm_token: str
