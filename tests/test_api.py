from math import perm
import pytest
import respx
import httpx
from galene.api.galene_api import GaleneAPI
from galene.api.models import GroupDefinition, UserDefinition
import os
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture
def galene_api():
    admin = os.getenv("API_ADMIN_LOGIN", default = "admin")
    password = os.getenv("API_ADMIN_PASSWORD", default ="password")
    return GaleneAPI("https://dty-s26-p2-galene.k8s-cloud.centralesupelec.fr", admin, password)

@pytest.mark.asyncio
async def test_list_groups(galene_api):
    groups = await galene_api.groups.list_groups()
    assert groups == ['night-watch']


@pytest.mark.asyncio
async def test_get_group(galene_api):
    print("TEST GET GROUP")
    group, etag = await galene_api.groups.get_group("night-watch")
    print(f"group description : {group}")
    print(f"group ETag : {etag}")

@pytest.mark.asyncio
async def test_update_group(galene_api):
    group, etag = await galene_api.groups.get_group("night-watch")
    print('etag 1 : ', etag)
    group.description = "night-watch group"
    await galene_api.groups.update_group("night-watch", group, etag)
    group, etag = await galene_api.groups.get_group("night-watch")
    print('etag 2 : ', etag)
    assert group.description == "night-watch group"


@pytest.mark.asyncio
async def test_create_group(galene_api):
    new_group = GroupDefinition(description="new group", public=False)
    await galene_api.groups.create_group("new_group", new_group)  
    groups = await galene_api.groups.list_groups()
    assert "new_group" in groups


@pytest.mark.asyncio
async def test_delete_group(galene_api):
    await galene_api.groups.delete_group("new_group")
    groups = await galene_api.groups.list_groups()
    assert "new_group" not in groups


@pytest.mark.asyncio
async def test_list_users(galene_api):
    users = await galene_api.users.list_users("night-watch")
    assert sorted(users) == ['vimes']

@pytest.mark.asyncio
async def test_create_user(galene_api):
    new_user = UserDefinition()
    await galene_api.users.update_user("night-watch", "test", new_user)
    await galene_api.users.set_user_password("night-watch", "test", "password")
    users = await galene_api.users.list_users("night-watch")
    assert "test" in users


@pytest.mark.asyncio
async def test_delete_user(galene_api):
    await galene_api.users.delete_user("night-watch", "test")
    assert "test" not in await galene_api.users.list_users("night-watch")



@pytest.mark.asyncio
async def test_get_user(galene_api):
    user = await galene_api.users.get_user("night-watch", "test")
    assert user.permissions == "observe"

    

@pytest.mark.asyncio
async def test_jwks_and_access_token(galene_api):
    import base64
    import random
    import string
    from galene.api.access_token import AccessToken, VideoGrants, TokenVerifier
    
    # 1. Generate a random 32-byte symmetric key
    raw_key = ''.join(random.choices(string.ascii_letters + string.digits, k=32)).encode()
    b64_key = base64.urlsafe_b64encode(raw_key).decode().rstrip("=")
    key_id = "test-key-1"
    
    jwks = {
        "keys": [
            {
                "kty": "oct",
                "kid": key_id,
                "k": b64_key,
                "alg": "HS256"
            }
        ]
    }
    
    # 2. Upload the keys
    await galene_api.groups.set_auth_keys("test-group", jwks)
    
    # 3. Create an Access Token
    server_url = galene_api.http.server_url
    token_str = AccessToken(raw_key.decode(), server_url) \
        .with_identity("token-user") \
        .add_grant(VideoGrants(room="test-group", permissions=["present", "op"])) \
        .to_jwt(kid=key_id)
        
    print(f"Generated JWT: {token_str}")
    
    # Verify the token decodes properly
    verifier = TokenVerifier(raw_key.decode())
    payload = verifier.verify(token_str, expected_audience=f"{server_url}/group/test-group/")
    assert payload["sub"] == "token-user"
    assert "present" in payload["permissions"]
    
    # 4. Connect via WebSocket and Join using the Token!
    import asyncio
    from galene.rtc.signal_client import SignalClient
    
    ws_url = "wss://dty-s26-p2-galene.k8s-cloud.centralesupelec.fr/ws"
    client = SignalClient()
    received_types = []
    
    async def on_msg(data):
        print(f"\n[JWT Auth] WS Received: {data.get('type')}")
        received_types.append(data.get("type"))
        
    client.on_message = on_msg
    
    try:
        await client.connect(ws_url)
        await client.send_handshake()
        
        # Join with the generated token instead of username/password
        print(f"Joining test-group with JWT token...")
        await client.send_join(group="test-group", token=token_str)
        
        await asyncio.sleep(2)
        
        assert "handshake" in received_types
        assert "joined" in received_types
        print("Successfully joined using JWT!")
        
    finally:
        await client.close()
        # 5. Cleanup keys
        await galene_api.groups.delete_auth_keys("test-group")


@pytest.mark.asyncio
async def test_list_tokens(galene_api):
    tokens = await galene_api.users.list_tokens("test-group", "token-user")
    print(tokens)