from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from fastapi.websockets import WebSocketState
from typing import Dict
from datetime import datetime, timezone
import logging
import json
from ast import literal_eval
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.requests import Request

# === Logging ===
logger = logging.getLogger("uvicorn")

# === Router setup ===
router = APIRouter(prefix="/api")

# === Constants ===
SERVER_ID = "server"

# === Templates ===
templates = Jinja2Templates(directory="templates")

# === Connection tracking ===
connected_servers: Dict[str, WebSocket] = {}
connected_robots: Dict[str, WebSocket] = {}
connected_users: Dict[str, WebSocket] = {}

server_metadata: Dict[str, Dict] = {}
robot_metadata: Dict[str, Dict] = {}
user_metadata: Dict[str, Dict] = {}

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


# === WebSocket Endpoint ===


@router.websocket("/ws/{id}")
async def websocket_endpoint(websocket: WebSocket, id: str):
    logger.info(f"New connection: {id}")

    ip = websocket.client.host
    connected_at = now_utc_iso()

    if id == SERVER_ID:
        await websocket.accept()

        if SERVER_ID in connected_servers:
            old_ws = connected_servers[SERVER_ID]
            logger.warning("Server already connected. Replacing it.")
            try:
                await send_safe(
                    old_ws, {"warning": "Another server has replaced this connection."}
                )
                await old_ws.close()
            except Exception as e:
                logger.error(f"Error closing old server connection: {e}")

        logger.info(f"New server connected: {id}")

        connected_servers[SERVER_ID] = websocket
        server_metadata[SERVER_ID] = {
            "ip": ip,
            "connected_at": connected_at,
            "last_seen": connected_at,
            "last_message": None,
            "status": "connected",
            "last_disconnected": None,
        }
        logger.info(f"Server connected from {ip}")

        try:
            while websocket.client_state == WebSocketState.CONNECTED:
                try:
                    message = await websocket.receive_text()
                    logger.info(f"Server sent: {message}")
                    data = json.loads(message)
                except json.JSONDecodeError:
                    try:
                        data = literal_eval(message)
                    except Exception as e:
                        logger.error("Invalid JSON from server.")
                        await send_safe(
                            websocket, {"error": "Invalid JSON Format", "level": 3}
                        )
                        continue

                server_metadata[SERVER_ID]["last_seen"] = now_utc_iso()
                server_metadata[SERVER_ID]["last_message"] = data

                target_robot = data.get("target_robot_id")
                target_user = data.get("target_user_id")

                if target_robot and (target_robot in connected_robots):
                    await send_safe(connected_robots[target_robot], data)
                    logger.info(
                        f"Forwarded message from server to robot: {target_robot}"
                    )
                elif target_user and (target_user in connected_users):
                    await send_safe(connected_users[target_user], data)
                    logger.info(f"Forwarded message from server to user: {target_user}")
                else:
                    logger.warning("No valid target found in server message")

        except WebSocketDisconnect:
            logger.warning("Server disconnected.")
        finally:
            for rid, ws in list(connected_robots.items()):
                try:
                    await send_safe(
                        ws,
                        {
                            "error": "Server disconnected.",
                            "level": 3,
                            "is_server_error": True,
                        },
                    )
                    await ws.close()
                    logger.info(f"Closed robot connection: {rid}")
                except Exception:
                    logger.warning(f"Error closing robot connection: {rid}")

                if rid in connected_robots:
                    connected_robots.pop(rid, None)

                if rid in robot_metadata:
                    robot_metadata.pop(rid, None)

            logger.info("Server disconnected, and removed all robot connections.")

            for uid, ws in list(connected_users.items()):
                try:
                    await send_safe(
                        ws,
                        {
                            "error": "Server disconnected.",
                            "level": 3,
                            "is_server_error": True,
                        },
                    )
                    await ws.close()
                    logger.info(f"Closed user connection: {uid}")
                except Exception:
                    logger.warning(f"Error closing user connection: {uid}")

                if uid in connected_users:
                    connected_users.pop(uid, None)

                if uid in user_metadata:
                    user_metadata.pop(uid, None)

            logger.info("Server disconnected, and removed all user connections.")

            if SERVER_ID in server_metadata:
                server_metadata[SERVER_ID]["status"] = "disconnected"
                server_metadata[SERVER_ID]["last_disconnected"] = now_utc_iso()

            if SERVER_ID in connected_servers:
                connected_servers.pop(SERVER_ID, None)

            logger.info("Server disconnected, and removed all of its connections.")

    elif id.startswith("bemo"):
        if SERVER_ID not in connected_servers:
            logger.warning(f"Robot {id} connected, but server is not connected.")
            await websocket.close(code=1008, reason="Server not connected")

            if id in connected_robots:
                connected_robots.pop(id, None)

            if id in robot_metadata:
                robot_metadata.pop(id, None)

            logger.info(f"Robot {id} disconnected, and removed from server.")
            return

        await websocket.accept()

        logger.info(f"New robot connected: {id}")

        connected_robots[id] = websocket
        robot_metadata[id] = {
            "ip": ip,
            "connected_at": connected_at,
            "last_seen": connected_at,
            "last_message": None,
            "status": "connected",
            "last_disconnected": None,
        }

        try:
            while websocket.client_state == WebSocketState.CONNECTED:
                try:
                    message = await websocket.receive_text()
                    logger.info(f"Robot sent: {message}")
                    data = json.loads(message)
                except json.JSONDecodeError:
                    try:
                        data = literal_eval(message)
                    except Exception as e:
                        logger.error("Invalid JSON from robot.")
                    await send_safe(
                        websocket, {"error": "Invalid JSON Format", "level": 3}
                    )
                    continue

                robot_metadata[id]["last_seen"] = now_utc_iso()
                robot_metadata[id]["last_message"] = data

                await send_safe(connected_servers[SERVER_ID], data)
                logger.info(f"Forwarded message from robot to server: {id}")

        except WebSocketDisconnect:
            logger.warning(f"Robot {id} disconnected.")
        finally:
            if id in robot_metadata:
                robot_metadata[id]["status"] = "disconnected"
                robot_metadata[id]["last_disconnected"] = now_utc_iso()

            if id in connected_robots:
                connected_robots.pop(id, None)

            logger.info(f"Robot {id} disconnected, and removed from server.")

    elif id.startswith("user"):
        if SERVER_ID not in connected_servers:
            logger.warning(f"User {id} connected, but server is not connected.")
            await websocket.close(code=1008, reason="Server not connected")

            if id in connected_users:
                connected_users.pop(id, None)

            if id in user_metadata:
                user_metadata.pop(id, None)

            logger.info(f"User {id} disconnected, and removed from server.")
            return

        await websocket.accept()

        logger.info(f"New user connected: {id}")

        connected_users[id] = websocket
        user_metadata[id] = {
            "ip": ip,
            "connected_at": connected_at,
            "last_seen": connected_at,
            "last_message": None,
            "status": "connected",
            "last_disconnected": None,
        }

        try:
            while websocket.client_state == WebSocketState.CONNECTED:
                try:
                    message = await websocket.receive_text()
                    logger.info(f"User sent: {message}")
                    data = json.loads(message)
                except json.JSONDecodeError:
                    try:
                        data = literal_eval(message)
                    except Exception as e:
                        logger.error("Invalid JSON from user.")
                        await send_safe(
                            websocket, {"error": "Invalid JSON Format", "level": 3}
                        )
                        continue

                user_metadata[id]["last_seen"] = now_utc_iso()
                user_metadata[id]["last_message"] = data
                await send_safe(connected_servers[SERVER_ID], data)
                logger.info(f"Forwarded message from user to server: {id}")

        except WebSocketDisconnect:
            logger.warning(f"User {id} disconnected.")
        finally:
            if id in user_metadata:
                user_metadata[id]["status"] = "disconnected"
                user_metadata[id]["last_disconnected"] = now_utc_iso()

            if id in connected_users:
                connected_users.pop(id, None)

            logger.info(f"User {id} disconnected, and removed from server.")

    else:
        logger.warning(f"Unknown connection: {id}")
        await websocket.close(code=1008, reason="Unknown connection type")


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
    return JSONResponse(
        content={
            "server": (
                format_device(SERVER_ID, server_metadata[SERVER_ID])
                if SERVER_ID in server_metadata
                else None
            ),
            "robots": [format_device(id, info) for id, info in robot_metadata.items()],
            "users": [format_device(id, info) for id, info in user_metadata.items()],
        }
    )


@router.get("/connected-devices", response_class=HTMLResponse)
async def get_connected_devices(request: Request):
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "server": (
                format_device(SERVER_ID, server_metadata[SERVER_ID])
                if SERVER_ID in server_metadata
                else None
            ),
            "robots": [format_device(id, info) for id, info in robot_metadata.items()],
            "users": [format_device(id, info) for id, info in user_metadata.items()],
        },
    )
