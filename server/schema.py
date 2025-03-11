from datetime import datetime
from typing import List
from pydantic import BaseModel

class Message(BaseModel):
    message_id: str
    message_type: str
    text: str
    timestamp: datetime

class Chat(BaseModel):
    chat_id: str
    chat_title: str
    type: str
    timestamp: datetime
    messages: List[Message]

class UserChat(BaseModel):
    user_id: str
    chats: List[Chat] = []

