from datetime import datetime
from pymongo import MongoClient
from uuid import uuid4
from dotenv import load_dotenv
from server.schema import Chat, UserChat, Message
import os
import logging

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("{asctime} - {name} - {levelname} - {message}", style="{")
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


class MongoManager:
    def __init__(self):
        logger.info("Initializing MongoManager")
        self.client = MongoClient(
            os.getenv("MONGO_URI"), maxPoolSize=50, retryWrites=True
        )
        self.db_name = self.client["colabi_chat"]
        self.collection = self.db_name["chats"]
        logger.info("MongoManager initialized successfully")

    def get_or_create_user(self, user_id):
        try:
            logger.info(f"Attempting to get/create user with ID: {user_id}")
            user_chat = self.collection.find_one({"user_id": user_id})

            if not user_chat:
                logger.info(f"User {user_id} not found. Creating new user.")
                user_chat = UserChat(user_id=user_id, chats=[])
                self.collection.insert_one(user_chat.model_dump())
                logger.info(f"New user {user_id} created successfully")
            else:
                logger.info(f"Found existing user {user_id}")

            return True

        except Exception as e:
            logger.error(f"Error in get_or_create_user: {str(e)}", exc_info=True)
            return False

    def get_chat(self, user_id: str, chat_id: str) -> dict:
        try:
            logger.info(f"Retrieving chat {chat_id} for user {user_id}")
            chat = self.collection.find_one(
                {"user_id": user_id},
                {"_id": 0, "chats": {"$elemMatch": {"chat_id": chat_id}}},
            )
            logger.info(f"Chat retrieval result: {'Found' if chat else 'Not found'}")
            return chat

        except Exception as e:
            logger.error(f"Error in get_chat: {str(e)}", exc_info=True)
            return False

    def create_chat(self, user_id: str, chat_id: str, type: str, message: str) -> dict:
        try:
            logger.info(
                f"Creating new chat {chat_id} for user {user_id} of type {type}"
            )
            new_chat = Chat(
                chat_id=chat_id,
                chat_title=message,
                type=type,
                timestamp=str(datetime.utcnow()),
                messages=[],
            )
            result = self.collection.update_one(
                {"user_id": user_id}, {"$push": {"chats": new_chat.model_dump()}}
            )
            logger.info(
                f"Chat creation {'successful' if result.modified_count > 0 else 'failed'}"
            )
            return result.modified_count > 0

        except Exception as e:
            logger.error(f"Error in create_chat: {str(e)}", exc_info=True)
            return False

    def add_message(self, user_id: int, chat_id: int, message: Message) -> bool:
        try:
            logger.info(f"Adding message to chat {chat_id} for user {user_id}")
            chat = self.get_chat_messages(user_id, chat_id)
            if not chat:
                logger.warning(f"Chat {chat_id} not found for user {user_id}")
                return False

            result = self.collection.update_one(
                {"user_id": user_id, "chats.chat_id": chat_id},
                {"$push": {"chats.$.messages": message.model_dump()}},
            )
            logger.info(
                f"Message addition {'successful' if result.modified_count > 0 else 'failed'}"
            )
            return result.modified_count > 0

        except Exception as e:
            logger.error(f"Error in add_message: {str(e)}", exc_info=True)
            return False

    def get_chat_messages(self, user_id: int, chat_id: int) -> dict:
        try:

            logger.info(f"Retrieving messages for chat {chat_id} of user {user_id}")
            chat = self.collection.find_one(
                {"user_id": user_id},
                {"_id": 0, "chats": {"$elemMatch": {"chat_id": chat_id}}},
            )
            if chat:
                chat = [{**chat,"timestamp": str(chat["timestamp"]),"messages": [{**message, "timestamp": str(message["timestamp"])}for message in chat.get("messages", [])]}for chat in chat["chats"]]
            logger.info(f"Messages retrieval {'successful' if chat else 'failed'}")
            return chat

        except Exception as e:
            logger.error(f"Error in get_chat_messages: {str(e)}", exc_info=True)
            return None

    def get_messages_for_chat(self, user_id: int, chat_id: int) -> dict:
        try:

            logger.info(f"Retrieving messages for chat {chat_id} of user {user_id}")
            chat = self.collection.find_one(
                {"user_id": user_id},
                {"_id": 0, "chats": {"$elemMatch": {"chat_id": chat_id}}},
            )
            if chat and "chats" in chat and chat["chats"]:
                messages = chat["chats"][0].get("messages", [])
                
                formatted_messages = [
                    {**message, "timestamp": str(message["timestamp"])} 
                    for message in messages
                ]
                
                result = formatted_messages
            else:
                result = []
        
            logger.info(f"Messages retrieval {'successful' if result else 'failed'}")
            return result
        
        except Exception as e:
            logger.error(f"Error in get_chat_messages: {str(e)}", exc_info=True)
            return None


    def get_all_chats(self, user_id: str):
        try:
            logger.info(f"Retrieving all chats for user {user_id}")

            chats = self.collection.find_one(
                {"user_id": user_id}, {"_id": 0, "chats.messages": 0}
            )
            logger.info(
                f"Retrieved {'some' if chats else 'no'} chats for user {user_id}"
            )
            if chats:
                chats  = [   
                    {
                          **chat,
                        "timestamp": str(chat["timestamp"]),
                    }
                    for chat in chats["chats"]] 

            return chats

        except Exception as e:
            logger.error(f"Error in get_all_chats: {str(e)}", exc_info=True)
            return None
