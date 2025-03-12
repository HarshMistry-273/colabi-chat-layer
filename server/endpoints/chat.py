import json
from datetime import datetime
from uuid import uuid4
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from db.mongo_manager import MongoManager
from db.connection import get_db_session
from sqlalchemy.orm import Session
from server.common import extract_json
from server.utils.normal_chat import normal_chat, clean_messages
from server.utils.log import logger
from server.utils.retrieve_context import retrieve_similar_docs, get_parsed_response
from server.utils.retrieve_data import retrieve_data
from server.utils.workflow_chat import workflow_chat, clean_workflow_messages
from server.schema import Message
# from server.utils.dynamicbot import DynamicBot
# from server.utils.chatbotprompts import *
# import os

# Web socket connection manager

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)


# API Router
chat_router = APIRouter()

# Connection Manager
manager = ConnectionManager()

# Db Manager
mongo_manager = MongoManager()


# Chat Web Socket
@chat_router.websocket("/chatlayer/{client_id}/{chat_id}")
async def chat_layer(
    websocket: WebSocket,
    client_id: str,
    chat_id: str,
    db: Session = Depends(get_db_session),
):
    try:
        await manager.connect(websocket)
        logger.info(f"WebSocket connection established - Client ID: {client_id}")
        # Commented code (Made by Utsav Davda) for workflow creation

        """File creation"""
        # user_output_file_path =f"{os.getcwd()}/userfiles/{client_id}_{chat_id}.txt"
        # print(user_output_file_path)
        # if not os.path.exists(os.path.join(os.getcwd(),'userfiles')):
        #     os.makedirs(os.path.join(os.getcwd(),'userfiles'))
        # with open(user_output_file_path,'w') as f:
        #     f.write("""{
        #     "workflow_title": "",
        #     "descKeyboardInterruptription": "",
        #     "business_area": "",
        #     "client_specific": (True or False),
        #     "schedule_type": (Instant, Scheduled, Recurring),
        #     "tasks": [ 
        #     ]
        #     }""")  

        """Bot Initialzation"""
        # Workflow_bot =  DynamicBot(user_output_file_path)

        while True:
            try:
                logger.debug(f"Awaiting message from client {client_id}")
                data = await websocket.receive_json()
                logger.info(
                    f"Received message from client {client_id} - Type: {data.get('type')}"
                )

                # Validate required fields
                if not all(key in data for key in ["type", "message"]):
                    logger.error(f"Invalid message format from client {client_id}")
                    await websocket.send_json(
                        {"error": "Invalid message format", "status": "error"}
                    )
                    continue

                # Get or create user and chat
                logger.debug(f"Processing user and chat for client {client_id}")
                if not mongo_manager.get_or_create_user(user_id=client_id):
                    logger.error(f"Failed to get/create user {client_id}")
                    await websocket.send_json(
                        {"error": "Failed to process user", "status": "error"}
                    )
                    continue

                # Get user chat
                logger.info(
                    f"Getting user chat for client {client_id} & chat {chat_id}"
                )
                chat = mongo_manager.get_chat(user_id=client_id, chat_id=chat_id)

                # Validate and add chat
                logger.info(
                    f"Validating and adding user chat for client {client_id} & chat {chat_id}"
                )
                if not chat and not mongo_manager.create_chat(
                    user_id=client_id, chat_id=chat_id, type=data["type"], message=data["message"]
                ):
                    logger.error(
                        f"Faile0d to create chat {chat_id} for user {client_id}"
                    )
                    await websocket.send_json(
                        {"error": "Failed to create chat", "status": "error"}
                    )
                    continue    

                # General chat
                if data["type"] == "general-support":
                    logger.info(
                        f"Processing general support message for client {client_id}"
                    )

                    # Create human message
                    message_id = str(uuid4())
                    current_time = str(datetime.utcnow())
                    human_message = Message(
                        message_id=message_id,
                        message_type="human",
                        text=data["message"],
                        timestamp=current_time,
                    )

                    # Validate and add human message in Db
                    if not mongo_manager.add_message(
                        user_id=client_id, chat_id=chat_id, message=human_message
                    ):
                        logger.error(
                            f"Failed to save human message for client {client_id}"
                        )
                        await websocket.send_json(
                            {"error": "Failed to save message", "status": "error"}
                        )
                        continue

                    # Retrireve context
                    logger.info(f"Retrieving context for client {client_id}")
                    context = retrieve_similar_docs(
                        data["message"], top_k=3, type=data["type"]
                    )
                    context = get_parsed_response(context=context)

                    # Get bot response
                    logger.debug(f"Generating bot response for client {client_id}")
                    bot_response = normal_chat(message=data["message"], context=context)

                    # Create bot response
                    bot_message = Message(
                        message_id=str(uuid4()),
                        message_type="ai",
                        text=bot_response,
                        timestamp=str(datetime.utcnow()),
                    )

                    # Validate and add bot message
                    if not mongo_manager.add_message(
                        user_id=client_id, chat_id=chat_id, message=bot_message
                    ):
                        logger.error(
                            f"Failed to save bot message for client {client_id}"
                        )
                        await websocket.send_json(
                            {"error": "Failed to save bot response", "status": "error"}
                        )
                        continue

                    # Send response to client
                    logger.info(f"Sending response to client {client_id}")
                    await websocket.send_json(
                        {"bot_message": bot_response, "status": "success"}
                    )

                # Workflow creation
                elif data["type"] == "workflow-creation":
                    logger.info(
                        f"Processing workflow creation message for client {client_id}"
                    )

                    # Empty initialization of entity      
                    entities = []

                    # Create human message
                    message_id = str(uuid4())
                    current_time = datetime.utcnow()
                    human_message = Message(
                        message_id=message_id,
                        message_type="human",
                        text=data["message"],
                        timestamp=current_time,
                    )
                    # user_response = data["message"]
                    # Validate and add human message
                    if not mongo_manager.add_message(
                        user_id=client_id, chat_id=chat_id, message=human_message
                    ):
                        logger.error(
                            f"Failed to save human message for client {client_id}"
                        )
                        await websocket.send_json(
                            {"error": "Failed to save message", "status": "error"}
                        )
                        continue
                    
                    business_areas = retrieve_data(db=db, type="business_area", user_id=client_id)
                    entities = [business_areas]

                    # Check and retrieve workflow_data
                    if data.get("workflow_data"):            
                        logger.info(
                            f"Processing workflow information for client {client_id}"
                        )
                        ids = data.get("workflow_data")
                        agent_ids = ids.get("agent_ids", [])
                        team_member_ids = ids.get("team_member_ids", [])
                        client_ids = ids.get("client_ids", [])
                        freelancer_ids = ids.get("freelancer_ids", [])

                        """ Workflow data retrieval """
                        # all_worker_ids = [("ai agents",agent_ids),("team ids",team_member_ids),("client ids",client_ids),("freelancer ids",freelancer_ids)]
                        # Workflow_bot.add_id(all_worker_ids)
                        
                        agent_data = retrieve_data(db=db, ids=agent_ids,  type="agents")
                        team_member_data = retrieve_data(
                            db=db,ids=team_member_ids, type="team_members"
                        )
                        client_data = retrieve_data(db=db, ids=client_ids, type="clients")
                        freelancer_data = retrieve_data(
                            db=db, ids=freelancer_ids, type="respondents"
                        )
                        
                        logger.info(f"Entities retrieved for client {client_id}")

                        entities.extend([agent_data, team_member_data, client_data, freelancer_data])
                        
                    # Retrieve context
                    logger.info(f"Retrieving context for client {client_id}")
                    context = retrieve_similar_docs(
                        data["message"], top_k=3, type=data["type"]
                    )
                    context = get_parsed_response(context=context)
                    
                    logger.debug(f"Generating bot response for client {client_id}")

                    # Check for entities and get bot response
                    if entities:
                        logger.info(f"In entities {entities}")
                        bot_response = workflow_chat(
                            message=data["message"], data=entities, context=context
                        )
                    # Check for context and get bot response
                    elif context:
                        bot_response = workflow_chat(
                            message=data["message"], context=context
                        )

                    """Bot response retrieval"""                     
                    # bot_response = Workflow_bot.chat(user_response)
                    
                    # Create bot message
                    bot_message = Message(
                        message_id=str(uuid4()),
                        message_type="ai",
                        text=bot_response,
                        timestamp=str(datetime.utcnow()),
                    )
                     
                    # Validate and add bot message
                    if not mongo_manager.add_message(
                        user_id=client_id, chat_id=chat_id, message=bot_message
                    ):
                        logger.error(
                            f"Failed to save bot message for client {client_id}"
                        )
                        await websocket.send_json(
                            {"error": "Failed to save bot response", "status": "error"}
                        )
                        continue

                    logger.info("checking the conditions")
                    workflow, is_workflow_generated = extract_json(bot_response=bot_response)
                    logger.info(is_workflow_generated)
                    if is_workflow_generated:

                        update_result = mongo_manager.update_chat(
                                        user_id=client_id, 
                                        chat_id=chat_id, 
                                        **workflow
                                    )
                        
                        if not update_result:
                            logger.error(f"Failed to update workflow for chat {chat_id}, client {client_id}")

                        await websocket.send_json(
                        {"bot_message": "Workflow Generated!",  "status": "success", **workflow}
                    )
                    else:
                        # Send response to client
                        logger.info(f"Sending response to client {client_id}")
                        await websocket.send_json(
                            {"bot_message": bot_response, "status": "success"}
                        )

                # Ai Employee creation
                elif data["type"] == "ai-employee-creation":
                    logger.info(                    
                        f"Processing ai employee creation message for client {client_id}"
                    )

                    # Create human message
                    message_id = str(uuid4())
                    current_time = datetime.utcnow()
                    human_message = Message(
                        message_id=message_id,
                        message_type="human",
                        text=data["message"],
                        timestamp=current_time,
                    )

                    # Validate and add human message
                    if not mongo_manager.add_message(
                        user_id=client_id, chat_id=chat_id, message=human_message
                    ):
                        logger.error(
                            f"Failed to save human message for client {client_id}"
                        )
                        await websocket.send_json(
                            {"error": "Failed to save message", "status": "error"}
                        )
                        continue
                    
                    logger.info(f"Generating bot response for client {client_id}")

                    bot_response = ""


                # Invlaid message type
                else:
                    logger.warning(
                        f"Unsupported message type from client {client_id}: {data['type']}"
                    )
                    await websocket.send_json(
                        {"error": "Unsupported message type", "status": "error"}
                    )

            except json.JSONDecodeError:
                logger.error(f"Invalid JSON received from client {client_id}")
                await websocket.send_json(
                    {"error": "Invalid JSON format", "status": "error"}
                )

    # Client disconnection
    except WebSocketDisconnect:
        logger.info(f"Client disconnected: {client_id}")
                              
    # External error
    except Exception as e:
        logger.error(
            f"Unexpected error for client {client_id}: {str(e)}", exc_info=True
        )

    #Cleanup
    finally:
        logger.info("PPP")
        clean_messages()
        clean_workflow_messages()
        logger.info(f"Cleaning up connection for client {client_id}")
        manager.disconnect(websocket)


# Get all chats
@chat_router.get("/chats/{client_id}")
def get_all_client_chats(client_id: str):
    try:
        # Get all chats
        logger.info(f"Getting chats for client {client_id}")
        chats = mongo_manager.get_all_chats(client_id)

        if not chats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No chats found!"
            )
        logger.info("Clients chats: {chats}")

        # Send response to client
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"data": chats, "error": "", "status": True},
        )

    except HTTPException as e:
        logger.error(f"Chat not found for client {client_id}")
        return JSONResponse(
            status_code=e.status_code,
            content={"data": e.detail, "error": "", "status": True},
        )

    except Exception as e:
        logger.error(f"Error getting chat for client {client_id}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"data": "An error occured", "error": str(e), "status": False},
        )

# Get chat by id
@chat_router.get("/chats/{client_id}/{chat_id}")
def retrieve_chat(client_id, chat_id):
    try:
        # Get chat with chat id
        logger.info(f"Getting chat for client {client_id} and chat id {chat_id}")
        chat = mongo_manager.get_messages_for_chat(client_id, chat_id)
        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No chat found!"
            )
        
        # Send response to client
        logger.info(f"Sending chat {chat_id} to client {client_id}")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"data": chat, "error": "", "status": True},
        )

    except HTTPException as e:
        logger.error(f"Chats {chat_id} for client {client_id} not found")
        return JSONResponse(
            status_code=e.status_code,
            content={"data": e.detail, "error": "", "status": True},
        )

    except Exception as e:
        logger.error(f"Error getting chat {chat_id} for client {client_id}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"data": "An error occured", "error": str(e), "status": False},
        )
