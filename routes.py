from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState
from typing import Dict
import logging
import json

# Set up logging
logger = logging.getLogger("uvicorn")

SERVER_ID = "server"
router = APIRouter(prefix="/api")
connected_devices: Dict[str, WebSocket] = {}

@router.websocket("/ws/{id}")
async def websocket_endpoint(websocket: WebSocket, id: str):
    logger.info(f"New connection: {id}")
    await websocket.accept()

    if id == SERVER_ID:
        if SERVER_ID in connected_devices:
            logger.error("Server is already connected.")
            await websocket.close()
            return

        logger.info("Server connected")
        connected_devices[id] = websocket

        try:
            while websocket.client_state == WebSocketState.CONNECTED:
                message = await websocket.receive_text()
                logger.info(f"Server sent: {message}")

                try:
                    data = json.loads(message)
                except json.JSONDecodeError:
                    logger.error("Invalid JSON format")
                    await websocket.send_text("Invalid JSON format.")
                    continue

                target_robot_id = data.get("target_robot_id")
                if target_robot_id in connected_devices:
                    await connected_devices[target_robot_id].send_text(message)
                    logger.info(f"Forwarded message to {target_robot_id}: {message}")
                else:
                    logger.warning(f"Robot {target_robot_id} not connected.")

        except WebSocketDisconnect:
            logger.warning("Server disconnected")
            connected_devices.pop(id, None)

    else:
        if SERVER_ID not in connected_devices:
            logger.error("Server is not connected. Cannot proceed.")
            await websocket.close()
            return

        logger.info(f"Robot connected: {id}")
        connected_devices[id] = websocket

        try:
            while websocket.client_state == WebSocketState.CONNECTED:
                message = await websocket.receive_text()
                logger.info(f"{id} sent: {message}")

                try:
                    data = json.loads(message)
                except json.JSONDecodeError:
                    logger.error("Invalid JSON format")
                    await websocket.send_text("Invalid JSON format.")
                    continue

                await connected_devices[SERVER_ID].send_text(message)
                logger.info(f"Forwarded message to server: {message}")

        except WebSocketDisconnect:
            logger.warning(f"{id} disconnected")
            connected_devices.pop(id, None)
