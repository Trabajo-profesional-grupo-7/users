from pydantic import BaseModel


class PostUser(BaseModel):
    username: str
    email: str
    password: str
    birthDate: str
