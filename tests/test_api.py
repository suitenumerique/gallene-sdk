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
    new_user = UserDefinition(permissions="present")
    await galene_api.users.update_user("test-group", "test", new_user)
    await galene_api.users.set_user_password("test-group", "test", "password")
    users = await galene_api.users.list_users("test-group")
    assert "test" in users


@pytest.mark.asyncio
async def test_delete_user(galene_api):
    await galene_api.users.delete_user("test-group", "test")
    assert "test" not in await galene_api.users.list_users("test-group")



@pytest.mark.asyncio
async def test_get_user(galene_api):
    user = await galene_api.users.get_user("night-watch", "test")
    assert user.permissions == "observe"


@pytest.mark.asyncio
async def test_list_tokens(galene_api):
    tokens = await galene_api.users.list_tokens("night-watch", "vimes")
    print(tokens)
    

