from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from fastapi.websockets import WebSocketState
from typing import Dict
from datetime import datetime, timezone
import logging
import json
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.requests import Request

# === Logging ===
logger = logging.getLogger("uvicorn")

# === Router setup ===
router = APIRouter(prefix="/api")

# === Constants ===
SERVER_ID = "server"

# === Connection tracking ===
connected_devices: Dict[str, WebSocket] = {}
device_metadata: Dict[str, Dict] = {}

# === Templates ===
templates = Jinja2Templates(directory="templates")

# === Utility ===

def now_utc_iso():
    return datetime.now(timezone.utc).isoformat()

def get_duration_seconds(connected_at_iso: str):
    connected_at = datetime.fromisoformat(connected_at_iso)
    now = datetime.now(timezone.utc)
    return int((now - connected_at).total_seconds())

async def send_safe(ws: WebSocket, data: dict):
    if ws.client_state == WebSocketState.CONNECTED:
        try:
            await ws.send_text(json.dumps(data))
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
    else:
        logger.warning("Attempted to send on a closed socket.")

async def forward_message_to_robot(target_id: str, message: str):
    sender_id = SERVER_ID
    
    if target_id in connected_devices:
        await send_safe(connected_devices[target_id], json.loads(message))
        logger.info(f"Forwarded from {sender_id} to {target_id}: {message}")
    else:
        logger.warning(f"Target '{target_id}' not connected.")
       
        await send_safe(connected_devices[sender_id], {
            "error": f"Target '{target_id}' not connected.",
            "level": 3,
            "src_robot_id": target_id,
            "is_server_error": True
        })


# === WebSocket Endpoint ===

@router.websocket("/ws/{id}")
async def websocket_endpoint(websocket: WebSocket, id: str):
    logger.info(f"New connection: {id}")
    await websocket.accept()

    ip = websocket.client.host
    connected_at = now_utc_iso()

    if id == SERVER_ID:
        if SERVER_ID in connected_devices:
            old_ws = connected_devices[SERVER_ID]
            logger.warning("Server already connected. Replacing it.")
            try:
                await send_safe(old_ws, {
                    "warning": "Another server has replaced this connection.",
                })
                await old_ws.close()
            except Exception as e:
                logger.error(f"Error closing old server connection: {e}")

        connected_devices[SERVER_ID] = websocket
        device_metadata[SERVER_ID] = {
            "ip": ip,
            "connected_at": connected_at,
            "last_seen": connected_at,
            "last_message": None,
            "status": "connected",
            "last_disconnected": None
        }
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
                
                device_metadata[SERVER_ID]["last_seen"] = now_utc_iso()
                device_metadata[SERVER_ID]["last_message"] = data

                
                target_id = data.get("target_robot_id")
                if target_id:
                    await forward_message_to_robot(target_id, message)
                else:
                    logger.warning("No 'target_robot_id' in message.")

        except WebSocketDisconnect:
            logger.warning("Server disconnected.")
        finally:
            logger.warning("Cleaning up all robot connections since server disconnected.")
            robot_ids = [rid for rid in connected_devices if rid != SERVER_ID]
            for rid in robot_ids:
                try:
                    await send_safe(connected_devices[rid], {
                        "error": "Server disconnected. Closing robot connection.",
                        "level": 3,
                        "is_server_error": True
                    })
                    await connected_devices[rid].close()
                    logger.info(f"Disconnected robot: {rid}")
                except Exception as e:
                    logger.error(f"Failed to disconnect robot {rid}: {e}")
                finally:
                    connected_devices.pop(rid, None)
                    device_metadata.pop(rid, None)
            
            device_metadata[SERVER_ID]["status"] = "disconnected"
            device_metadata[SERVER_ID]["last_disconnected"] = now_utc_iso()
            
            metadata = device_metadata.get(SERVER_ID, {})
            connected_at = metadata.get("connected_at")

            if connected_at:
                duration = get_duration_seconds(connected_at)
                logger.info(f"Server was connected for {duration} seconds")
            else:
                logger.warning("No 'connected_at' info for server")

            connected_devices.pop(SERVER_ID, None)
            device_metadata.pop(SERVER_ID, None)

    else:
        if SERVER_ID not in connected_devices:
            logger.error("Server not connected. Rejecting robot.")
            await send_safe(websocket, {
                "error": "Server not connected.",
                "level": 3,
                "target_robot_id": id,
                "is_server_error": True
            })
            await websocket.close()
            return

        connected_devices[id] = websocket
        device_metadata[id] = {
            "ip": ip,
            "connected_at": connected_at,
            "last_seen": connected_at,
            "last_message": None,
            "status": "connected",
            "last_disconnected": None
        }

        logger.info(f"Robot '{id}' connected from {ip}")

        try:
            while websocket.client_state == WebSocketState.CONNECTED:
                try:
                    message = await websocket.receive_text()

                    logger.info(f"{id} sent: {message}")
                    data = json.loads(message)
                    device_metadata[id]["last_seen"] = now_utc_iso()
                    device_metadata[id]["last_message"] = data
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON from robot {id}.")
                    await send_safe(websocket, {
                        "error": "Invalid JSON Format",
                        "level": 3,
                        "target_robot_id": id,
                        "is_server_error": True
                    })
                    continue

                await send_safe(connected_devices[SERVER_ID], data)
                logger.info(f"Forwarded message from {id} to server.")

        except WebSocketDisconnect:
            logger.warning(f"Robot '{id}' disconnected.")
        finally:
            device_metadata[id]["status"] = "disconnected"
            device_metadata[id]["last_disconnected"] = now_utc_iso()
            
            metadata = device_metadata.get(id, {})
            connected_at = metadata.get("connected_at")

            if connected_at:
                duration = get_duration_seconds(connected_at)
                logger.info(f"Robot '{id}' was connected for {duration} seconds")
            else:
                logger.warning(f"No 'connected_at' info for robot '{id}'")

            connected_devices.pop(id, None)
            device_metadata.pop(id, None)            


# === REST Endpoint for status ===

def format_device(device_id, info):
    return {
        "id": device_id,
        "ip": info["ip"],
        "connected_at": info["connected_at"],
        "duration": get_duration_seconds(info["connected_at"]),
        "status": info.get("status", "unknown"),
        "last_seen": info.get("last_seen"),
        "last_message": info.get("last_message"),
        "last_disconnected": info.get("last_disconnected"),
    }

@router.get("/connected-devices/json", response_class=JSONResponse)
async def get_connected_devices_json():
    return JSONResponse(content={
        "server": format_device(SERVER_ID, device_metadata[SERVER_ID])
        if SERVER_ID in device_metadata else None,
        "robots": [
            format_device(device_id, info)
            for device_id, info in device_metadata.items()
            if device_id != SERVER_ID
        ]
    })
    
@router.get("/connected-devices", response_class=HTMLResponse)
async def get_connected_devices(request: Request):
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "server": format_device(SERVER_ID, device_metadata[SERVER_ID])
        if SERVER_ID in device_metadata else None,
        "robots": [
            format_device(device_id, info)
            for device_id, info in device_metadata.items()
            if device_id != SERVER_ID
        ]
    })


