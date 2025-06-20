from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState
from fastapi.responses import JSONResponse
from typing import Dict
from datetime import datetime
import logging
import json

# === Logging ===
logger = logging.getLogger("uvicorn")

# === Router setup ===
router = APIRouter(prefix="/api")

# === Constants ===
SERVER_ID = "server"

# === Connection tracking ===
connected_devices: Dict[str, WebSocket] = {}
device_metadata: Dict[str, Dict] = {}


# === Utility functions ===

async def send_safe(ws: WebSocket, data: dict):
    """Send JSON safely over a WebSocket."""
    if ws.client_state == WebSocketState.CONNECTED:
        try:
            await ws.send_text(json.dumps(data))
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
    else:
        logger.warning("Attempted to send on a closed socket.")


async def forward_message(sender_id: str, target_id: str, message: str):
    """Forward a message to another connected client."""
    if target_id in connected_devices:
        await send_safe(connected_devices[target_id], json.loads(message))
        logger.info(f"Forwarded from {sender_id} to {target_id}: {message}")
    else:
        logger.warning(f"Target '{target_id}' not connected.")
        await send_safe(connected_devices[sender_id], {
            "error": f"Target '{target_id}' not connected.",
            "level": 2,
            "from": sender_id,
            "to": target_id,
        })


# === WebSocket Endpoint ===

@router.websocket("/ws/{id}")
async def websocket_endpoint(websocket: WebSocket, id: str):
    logger.info(f"New connection: {id}")
    await websocket.accept()

    ip = websocket.client.host
    connected_at = datetime.utcnow().isoformat() + "Z"

    # === SERVER CONNECTING ===
    if id == SERVER_ID:
        if SERVER_ID in connected_devices:
            old_ws = connected_devices[SERVER_ID]
            logger.warning("Server already connected. Replacing it.")
            try:
                await send_safe(old_ws, {
                    "warning": "Another server has replaced this connection.",
                    "level": 2
                })
                await old_ws.close()
            except Exception as e:
                logger.error(f"Error closing old server connection: {e}")

        connected_devices[SERVER_ID] = websocket
        device_metadata[SERVER_ID] = {"ip": ip, "connected_at": connected_at}
        logger.info(f"Server connected from {ip}")

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
                    logger.warning("No 'target_robot_id' in message.")

        except WebSocketDisconnect:
            logger.warning("Server disconnected.")
        finally:
            connected_devices.pop(SERVER_ID, None)
            device_metadata.pop(SERVER_ID, None)

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
        device_metadata[id] = {"ip": ip, "connected_at": connected_at}
        logger.info(f"Robot '{id}' connected from {ip}")

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
            device_metadata.pop(id, None)


# === REST API Endpoint ===

@router.get("/connected-devices")
async def get_connected_devices():
    """Return info about currently connected devices."""
    robots = {
        device_id: info
        for device_id, info in device_metadata.items()
        if device_id != SERVER_ID
    }

    return JSONResponse(
        content={
            "server_connected": SERVER_ID in connected_devices,
            "server_info": device_metadata.get(SERVER_ID),
            "robots_connected": robots,
            "robot_count": len(robots)
        }
    )
