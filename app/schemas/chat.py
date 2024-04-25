from pydantic import BaseModel


class Chat(BaseModel):
    user_id: str
    thread_id: str
    assistant_id: str
