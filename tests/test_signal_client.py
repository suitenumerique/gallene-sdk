import asyncio
import json
import pytest
import pytest_asyncio
import websockets
from galene.rtc.signal_client import SignalClient

class MockGaleneServer:
    def __init__(self):
        self.received = []
        self.connected_ws = None
        self.server = None

    async def handler(self, websocket):
        self.connected_ws = websocket
        try:
            async for message in websocket:
                data = json.loads(message)
                self.received.append(data)
        except websockets.exceptions.ConnectionClosed:
            pass

    async def start(self):
        self.server = await websockets.serve(self.handler, "localhost", 0)
        return f"ws://localhost:{self.server.sockets[0].getsockname()[1]}"

    async def stop(self):
        if self.server:
            self.server.close()
            await self.server.wait_closed()

    async def push(self, data: dict):
        if self.connected_ws:
            await self.connected_ws.send(json.dumps(data))


@pytest_asyncio.fixture
async def mock_server():
    server = MockGaleneServer()
    url = await server.start()
    yield server, url
    await server.stop()


@pytest.mark.asyncio
async def test_signal_client_connection(mock_server):
    server, url = mock_server
    client = SignalClient()
    
    await client.connect(url)
    assert client._ws is not None
    
    await client.close()
    assert client._ws is None


@pytest.mark.asyncio
async def test_signal_client_handshake_and_join(mock_server):
    server, url = mock_server
    client = SignalClient()
    
    await client.connect(url)
    await client.send_handshake()
    await client.send_join("test-room", username="margot", password = "margot")
    
    # Give some time for messages to arrive
    await asyncio.sleep(0.1)
    
    assert len(server.received) == 2
    assert server.received[0]["type"] == "handshake"
    assert server.received[1]["type"] == "join"
    assert server.received[1]["group"] == "test-room"
    await client.close()



@pytest.mark.asyncio
async def test_signal_client_auto_pong(mock_server):
    server, url = mock_server
    client = SignalClient()
    
    await client.connect(url)
    
    # Server sends a ping
    await server.push({"type": "ping"})
    
    # Client should automatically send back a pong
    await asyncio.sleep(0.1)
    
    assert any(msg.get("type") == "pong" for msg in server.received)
    await client.close()


@pytest.mark.asyncio
async def test_signal_client_callback(mock_server):
    server, url = mock_server
    client = SignalClient()
    
    received_data = []
    async def on_message(data):
        received_data.append(data)
    
    client.on_message = on_message
    
    await client.connect(url)
    
    # Server sends a chat message
    chat_msg = {"type": "chat", "value": "hello"}
    await server.push(chat_msg)
    
    # Wait for callback
    await asyncio.sleep(0.1)
    
    assert len(received_data) == 1
    assert received_data[0] == chat_msg
    
    await client.close()




@pytest.mark.asyncio
async def test_galene_live_connection():
    # 1. CHANGE THIS to your actual Galene WebSocket URL
    # If your group is at https://galene.example.com/group/test/
    # The endpoint is usually wss://galene.example.com/ws
    ws_url = "wss://dty-s26-p2-galene.k8s-cloud.centralesupelec.fr/ws" 
    
    client = SignalClient()
    
    # Track messages received from the real server
    received_types = []
    
    async def on_msg(data):
        print(f"\n[LIVE] Received: {data.get('type')}")
        print(data)
        received_types.append(data.get("type"))

    client.on_message = on_msg
    
    try:
        print(f"\nConnecting to {ws_url}...")
        await client.connect(ws_url)
        
        print("Sending Handshake...")
        await client.send_handshake()
        
        print("Joining 'test-group'...")
        await client.send_join(group="test-group", username="test2", password="password")
        
        # Wait a few seconds for Galene to respond
        await asyncio.sleep(2)
        
        # Verify we got a 'handshake' and 'joined' response from the real server
        assert "handshake" in received_types
        assert "joined" in received_types

        print("Sending Ping...")
        await client.send({"type": "ping"})
        
        # Wait a bit for the pong
        await asyncio.sleep(2)
        
        # Verify we got a pong back
        print("Pong received successfully!")

        print("Sending Chat Message...")
        await client.send_chat("Hello from Python SDK!")
        
        print("\n[LIVE] Monitoring connection for 60 seconds...")
        print("You should see server pings and other events here:")
        for i in range(120):
            await asyncio.sleep(1)
            if i % 10 == 0 and i > 0:
                print(f"--- {120-i} seconds remaining ---")
        
    finally:
        await client.close()
