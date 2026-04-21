import time
import pytest
import jwt
import random
import string
from freezegun import freeze_time
from galene.api.access_token import AccessToken, VideoGrants, TokenVerifier

def test_access_token_generation():
    key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=32))
    server_url = "https://galene.example.com"
    identity = "test-user"
    room = "test-room"
    permissions = ["present", "op"]
    
    with freeze_time("2024-01-01 12:00:00"):
        token = AccessToken(key, server_url) \
            .with_identity(identity) \
            .add_grant(VideoGrants(room=room, permissions=permissions)) \
            .to_jwt()
        
        decoded = jwt.decode(token, key, algorithms=["HS256"], audience=f"{server_url}/group/{room}/")
        
        assert decoded["sub"] == identity
        assert decoded["permissions"] == permissions
        assert decoded["iat"] == int(time.time())
        assert decoded["exp"] == int(time.time()) + 3600

def test_access_token_custom_ttl():
    key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=32))
    server_url = "https://galene.example.com"
    ttl = 7200
    
    with freeze_time("2024-01-01 12:00:00"):
        token = AccessToken(key, server_url) \
            .with_identity("user") \
            .add_grant(VideoGrants(room="room", permissions=[])) \
            .with_ttl(ttl) \
            .to_jwt()
        
        decoded = jwt.decode(token, key, algorithms=["HS256"], options={"verify_aud": False})
        assert decoded["exp"] == decoded["iat"] + ttl

def test_access_token_missing_fields():
    token = AccessToken(''.join(random.choices(string.ascii_uppercase + string.digits, k=32)), "url")
    
    with pytest.raises(ValueError, match="VideoGrants .* must be provided"):
        token.to_jwt()
        
    token.add_grant(VideoGrants(room="room", permissions=[]))
    with pytest.raises(ValueError, match="Identity .* must be provided"):
        token.to_jwt()

def test_token_verifier_success():
    key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=32))
    server_url = "https://galene.example.com"
    room = "room"
    audience = f"{server_url}/group/{room}/"
    
    token = AccessToken(key, server_url) \
        .with_identity("user") \
        .add_grant(VideoGrants(room=room, permissions=["op"])) \
        .to_jwt()
    
    verifier = TokenVerifier(key)
    payload = verifier.verify(token, expected_audience=audience)
    
    assert payload["sub"] == "user"
    assert payload["aud"] == audience

def test_token_verifier_invalid_audience():
    key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=32))
    token = AccessToken(key, "https://galene.com") \
        .with_identity("user") \
        .add_grant(VideoGrants(room="room1", permissions=[])) \
        .to_jwt()
    
    verifier = TokenVerifier(key)
    # Audience for room1 will be https://galene.com/group/room1/
    with pytest.raises(ValueError, match="Invalid token: Audience doesn't match"):
        verifier.verify(token, expected_audience="https://galene.com/group/room2/")

def test_server_url_trailing_slash():
    # URL with trailing slash should be normalized to remove it in the audience
    key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=32))
    token = AccessToken(key, "https://galene.com/") \
        .with_identity("user") \
        .add_grant(VideoGrants(room="room", permissions=[])) \
        .to_jwt()
    
    decoded = jwt.decode(token, key, algorithms=["HS256"], options={"verify_aud": False})
    # audience = "https://galene.com/group/room/" (server_url rstripped slash + /group/room/)
    assert decoded["aud"] == "https://galene.com/group/room/"
