from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict
import random
import time
import logging
import json
import os

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

AUDIO_SAVE_DIR = "received_audio"
os.makedirs(AUDIO_SAVE_DIR, exist_ok=True)

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

                    return_dict = {
                        "robot_id": robot_id,
                        "response": random.choice(friendly_responses),
                        "data": data
                    }

                    await websocket.send_json(return_dict)
                    logger.info(f"{robot_id} - Sent response: {return_dict}")

                elif binary_data:
                    logger.info(f"{robot_id} - Received binary audio data")

                    # Save audio to file
                    timestamp = int(time.time())
                    filename = f"{robot_id}_{timestamp}.wav"
                    filepath = os.path.join(AUDIO_SAVE_DIR, filename)

                    with open(filepath, "wb") as f:
                        f.write(binary_data)

                    logger.info(f"{robot_id} - Saved audio to: {filepath}")
                    await websocket.send_text(f"Audio received and saved as {filename}")

                else:
                    logger.warning(f"{robot_id} - No valid data received")
                    continue

            except json.JSONDecodeError:
                logger.error(f"{robot_id} - Invalid JSON format")
                await websocket.send_text("Invalid JSON format.")
            except Exception as e:
                logger.exception(f"{robot_id} - Unexpected error: {e}")
                await websocket.send_text(f"Error: {str(e)}")

    except WebSocketDisconnect:
        logger.warning(f"{robot_id} disconnected")
        connected_robots.pop(robot_id, None)
