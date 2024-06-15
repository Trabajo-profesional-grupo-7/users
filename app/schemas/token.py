from pydantic import BaseModel


class Token(BaseModel):
    token: str
    refresh_token: str
    token_type: str
