from math import perm
import pytest
import respx
import httpx
from galene.api.galene_api import GaleneAPI
from galene.api.models import GroupDefinition, UserDefinition
import os
from dotenv import load_dotenv

load_dotenv()

#PYTHONPATH=galene-api:galene-rtc uv run pytest -s tests/test_api.py -k test_list_group
@pytest.fixture
def galene_api():
    admin = os.getenv("API_ADMIN_LOGIN", default = "admin")
    password = os.getenv("API_ADMIN_PASSWORD", default ="password")
    return GaleneAPI("https://galene.dty-s26-p2-galene.k8s-cloud.centralesupelec.fr", admin, password)


@pytest.mark.asyncio
async def test_list_groups(galene_api):
    groups = await galene_api.groups.list_groups()
    print(groups)


@pytest.mark.asyncio
async def test_get_group(galene_api):
    print("TEST GET GROUP")
    group, etag = await galene_api.groups.get_group("test-group")
    print(f"group description : {group}")
    print(f"group ETag : {etag}")



@pytest.mark.asyncio
async def test_update_group(galene_api):
    group, etag = await galene_api.groups.get_group("test-group")
    print('etag 1 : ', etag)
    defi = group.model_dump(exclude_unset = True)
    new = {'permissions' : ["op"]}
    update = {**defi, **new}
    await galene_api.groups.update_group("test-group", update, etag = etag)
    group, etag = await galene_api.groups.get_group("test-group")
    print('etag 2 : ', etag)
    assert "op" in group.permissions



@pytest.mark.asyncio
async def test_create_group(galene_api):
    new_group = GroupDefinition(description="new group", public=False)
    await galene_api.groups.create_group("wjr-woua-eba", new_group)  
    groups = await galene_api.groups.list_groups()
    assert "wjr-woua-eba" in groups




@pytest.mark.asyncio
async def test_delete_group(galene_api):
    await galene_api.groups.delete_group("new_group")
    groups = await galene_api.groups.list_groups()
    assert "new_group" not in groups




@pytest.mark.asyncio
async def test_list_users(galene_api):
    users = await galene_api.users.list_users("wym-pxmn-eiw")
    print(f"users : {users}")

@pytest.mark.asyncio
async def test_create_user(galene_api):
    new_user = UserDefinition(permissions=["op", "present", "message"])
    await galene_api.users.update_user("evb-lfuf-pwz", "vimes", new_user)
    await galene_api.users.set_user_password("evb-lfuf-pwz", "vimes", "sybil")
    users = await galene_api.users.list_users("evb-lfuf-pwz")
    print(f'users : {users}')
    assert "vimes" in users


@pytest.mark.asyncio
async def test_delete_user(galene_api):
    await galene_api.users.delete_user("test-group", "test2")
    assert "test2" not in await galene_api.users.list_users("test-group")



@pytest.mark.asyncio
async def test_get_user(galene_api):
    user = await galene_api.users.get_user("test-group", "test")
    print(user)
    #assert user.permissions == "observe"




@pytest.mark.asyncio
async def test_update_user(galene_api):
    user = await galene_api.users.get_user("test-group", "test")
    print('user : ', user)
    user.permissions = ["present"]
    await galene_api.users.update_user("test-group", "test", user)
    user = await galene_api.users.get_user("test-group", "test")
    print('user now: ', user)
    assert user.permissions == ["present"]


@pytest.mark.asyncio
async def test_send_key(galene_api):
    import random
    import string
    await galene_api.groups.set_auth_keys("night-watch", "QBIBC0mkQn81WfoeAYEE7iJW1t9WzKPh")

@pytest.mark.asyncio
async def test_generate_token(galene_api):
    from galene.api.access_token import AccessToken, VideoGrants, TokenVerifier
    token = AccessToken("QBIBC0mkQn81WfoeAYEE7iJW1t9WzKPh", galene_api.http.server_url).with_identity("token-user").add_grant(VideoGrants(room="gii-mdyz-yzy", permissions= ["present"])).to_jwt(kid="JWT-HS256-key")
    print('token : ', token)


@pytest.mark.asyncio
async def test_delete_keys(galene_api):
    await galene_api.groups.delete_auth_keys("night-watch")
    

@pytest.mark.asyncio
async def test_list_tokens(galene_api):
    tokens = await galene_api.users.list_tokens("night-watch", "token-user")
    print(tokens)
