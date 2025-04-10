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
                text_data = await websocket.receive_json()
                data = json.loads(text_data)
                logger.info(f"{robot_id} sent: {data}")

                index = int(data.get("index", -1))
                if 0 <= index < len(friendly_responses):
                    await websocket.send_text(friendly_responses[index])
                else:
                    error_msg = f"Invalid index: {index}"
                    logger.warning(f"{robot_id} - {error_msg}")
                    await websocket.send_text(error_msg)
            except json.JSONDecodeError:
                logger.error(f"{robot_id} - Invalid JSON")
                await websocket.send_text("Invalid JSON format.")
            except Exception as e:
                logger.exception(f"{robot_id} - Unexpected error: {e}")
                await websocket.send_text(f"Error: {str(e)}")
    except WebSocketDisconnect:
        logger.warning(f"{robot_id} disconnected")
        connected_robots.pop(robot_id, None)
