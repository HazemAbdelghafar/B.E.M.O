from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict
import random
import time
import logging
import json

# Use uvicorn logger to ensure logs appear on Render
logger = logging.getLogger("uvicorn")

random.seed(time.time())

friendly_responses = [
    "Hello! I'm here to assist you.",
    "Greetings! How can I help you today?",
    "Hi there! What can I do for you?",
    "Hey! Ready to assist you.",
    "Hello! How may I help you today?"
]

router = APIRouter(prefix="/api")

connected_robots: Dict[str, WebSocket] = {}

@router.websocket("/ws/{robot_id}")
async def websocket_endpoint(websocket: WebSocket, robot_id: str):
    logger.info(f"New connection: {robot_id}")
    await websocket.accept()
    connected_robots[robot_id] = websocket
    logger.info(f"Robot connected: {robot_id}")

    try:
        while True:
            try:
                message = await websocket.receive()
                text_data = message.get("text", "")
                binary_data = message.get("bytes", b"")
                
                if text_data:
                    logger.info(f"{robot_id} - Received text data: {text_data}")
                    data = json.loads(text_data)
                elif binary_data:
                    logger.info(f"{robot_id} - Received binary data")
                    data = json.loads(binary_data.decode("utf-8"))
                else:
                    logger.warning(f"{robot_id} - No valid data received")
                    continue
                
                return_dict = {
                    "robot_id": robot_id,
                    "response": random.choice(friendly_responses),
                    "data": data
                }
                
                await websocket.send_json(return_dict)
                logger.info(f"{robot_id} - Sent response: {return_dict}")
            except json.JSONDecodeError:
                logger.error(f"{robot_id} - Invalid JSON")
                await websocket.send_text("Invalid JSON format.")
            except Exception as e:
                logger.exception(f"{robot_id} - Unexpected error: {e}")
                await websocket.send_text(f"Error: {str(e)}")
    except WebSocketDisconnect:
        logger.warning(f"{robot_id} disconnected")
        connected_robots.pop(robot_id, None)
