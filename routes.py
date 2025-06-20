from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState
from typing import Dict
import logging
import json

logger = logging.getLogger("uvicorn")
router = APIRouter(prefix="/api")

SERVER_ID = "server"
connected_devices: Dict[str, WebSocket] = {}


# === Utility Functions ===

async def send_safe(ws: WebSocket, data: dict):
    """Safely send JSON data over a WebSocket."""
    if ws.client_state == WebSocketState.CONNECTED:
        try:
            await ws.send_text(json.dumps(data))
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
    else:
        logger.warning("Attempted to send message to a closed socket.")


async def forward_message(sender_id: str, target_id: str, message: str):
    """Forward message to the target client."""
    if target_id in connected_devices:
        await send_safe(connected_devices[target_id], json.loads(message))
        logger.info(f"Forwarded message from {sender_id} to {target_id}: {message}")
    else:
        logger.warning(f"Target '{target_id}' not connected.")
        await send_safe(connected_devices[sender_id], {
            "error": f"Target '{target_id}' not connected.",
            "level": 2,
            "from": sender_id,
            "to": target_id,
        })


# === Main WebSocket Handler ===

@router.websocket("/ws/{id}")
async def websocket_endpoint(websocket: WebSocket, id: str):
    logger.info(f"New connection: {id}")
    await websocket.accept()

    # === SERVER CONNECTING ===
    if id == SERVER_ID:
        if SERVER_ID in connected_devices:
            old_server = connected_devices[SERVER_ID]
            logger.warning("Previous server is already connected. Replacing it.")
            try:
                await send_safe(old_server, {
                    "warning": "Another server connection has replaced this one.",
                    "level": 2
                })
                await old_server.close()
            except Exception as e:
                logger.error(f"Failed to close old server connection: {e}")

        connected_devices[SERVER_ID] = websocket
        logger.info("Server connected and ready.")

        try:
            while websocket.client_state == WebSocketState.CONNECTED:
                try:
                    message = await websocket.receive_text()
                    logger.info(f"Server sent: {message}")
                    data = json.loads(message)
                except json.JSONDecodeError:
                    logger.error("Invalid JSON from server.")
                    await send_safe(websocket, {"error": "Invalid JSON Format", "level": 3})
                    continue

                target_id = data.get("target_robot_id")
                if target_id:
                    await forward_message(SERVER_ID, target_id, message)
                else:
                    logger.warning("No 'target_robot_id' in server message.")

        except WebSocketDisconnect:
            logger.warning("Server disconnected.")
        finally:
            connected_devices.pop(SERVER_ID, None)

    # === ROBOT CONNECTING ===
    else:
        if SERVER_ID not in connected_devices:
            logger.error("Server not connected. Rejecting robot.")
            await send_safe(websocket, {
                "error": "Server not connected.",
                "level": 3,
                "target_robot_id": id
            })
            await websocket.close()
            return

        connected_devices[id] = websocket
        logger.info(f"Robot connected: {id}")

        try:
            while websocket.client_state == WebSocketState.CONNECTED:
                try:
                    message = await websocket.receive_text()
                    logger.info(f"{id} sent: {message}")
                    data = json.loads(message)
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON from robot {id}.")
                    await send_safe(websocket, {
                        "error": "Invalid JSON Format",
                        "level": 3,
                        "target_robot_id": id
                    })
                    continue

                await send_safe(connected_devices[SERVER_ID], data)
                logger.info(f"Forwarded message from {id} to server.")

        except WebSocketDisconnect:
            logger.warning(f"Robot '{id}' disconnected.")
        finally:
            connected_devices.pop(id, None)
