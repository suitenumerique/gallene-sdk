import asyncio
import json
import logging
import uuid
import websockets
from typing import Optional, Callable, Dict, Any, Awaitable

logger = logging.getLogger(__name__)

class SignalClient:
    """
    Handles the JSON-over-WebSocket signaling connection to Galene.
    """
    def __init__(self, client_id: Optional[str] = None):
        self.client_id = client_id or str(uuid.uuid4())
        self._ws: Optional[websockets.WebSocketClientProtocol] = None
        self._receive_task: Optional[asyncio.Task] = None
        # Callback for when a message is received (typically hooked up by RTCEngine/Room)
        self.on_message: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None

    async def connect(self, ws_url: str):
        """Builds the websocket connection and starts the read loop."""
        logger.info(f"Connecting to signaling server: {ws_url}")
        self._ws = await websockets.connect(ws_url)
        self._receive_task = asyncio.create_task(self._receive_loop())

    async def _receive_loop(self):
        """Continuously reads from the WebSocket."""
        try:
            async for message in self._ws:
                try:
                    data = json.loads(message)
                except json.JSONDecodeError:
                    logger.warning(f"Received invalid JSON: {message}")
                    continue
                
                # Galene spec: "A peer may at any time send a ping... must reply with a pong"
                if data.get("type") == "ping":
                    logger.debug("Received ping, sending pong")
                    await self.send({"type": "pong"})
                    continue
                
                if self.on_message:
                    # Dispatch to the upper layer
                    asyncio.create_task(self.on_message(data))

        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket connection closed")
        except Exception as e:
            logger.error(f"Error in receive loop: {e}")

    async def send(self, data: Dict[str, Any]):
        """Sends a JSON dictionary over the WebSocket."""
        if not self._ws:
            raise RuntimeError("WebSocket is not connected")
        logger.debug(f"Sending: {data}")
        await self._ws.send(json.dumps(data))


    async def send_chat(self, message: str, dest: str = ""):
        """Sends a chat message."""
        msg = {
            "type": "chat",
            "kind": "",
            "value": message
        }
        if dest:
            msg["dest"] = dest
        await self.send(msg)

    async def send_handshake(self):
        """Sends the initial protocol handshake."""
        msg = {
            "type": "handshake",
            "version": ["2"],
            "id": self.client_id
        }
        await self.send(msg)

    async def send_join(self, group: str, username: str = "", password: str = "", token: str = ""):
        """Requests to join a group."""
        msg = {
            "type": "join",
            "kind": "join",
            "group": group,
        }
        if token:
            msg["token"] = token
        else:
            msg["username"] = username
            msg["password"] = password
            
        await self.send(msg)

    async def close(self):
        """Gracefully shuts down the connection."""
        if self._receive_task:
            self._receive_task.cancel()
        if self._ws:
            await self._ws.close()
            self._ws = None
