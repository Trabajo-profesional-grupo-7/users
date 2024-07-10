from pydantic import BaseModel


class Chat(BaseModel):
    user_id: int
    thread_id: str
    assistant_id: str
