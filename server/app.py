from server.endpoints.chat import chat_router
from server.endpoints.upload import upload_router
from fastapi import APIRouter

app_router = APIRouter()

app_router.include_router(chat_router)
app_router.include_router(upload_router)