import pytest
import respx
import httpx
from galene.api.galene_api import GaleneAPI
from galene.api.models import GroupDefinition, UserDefinition

@pytest.fixture
def galene_api():
    return GaleneAPI("https://localhost:8443", "admin", "secret")

@pytest.mark.asyncio
async def test_list_groups(galene_api):
    with respx.mock:
        respx.get("https://localhost:8443/galene-api/v0/.groups/").respond(
            json=["group1", "group2"]
        )
        groups = await galene_api.groups.list_groups()
        assert groups == ["group1", "group2"]

@pytest.mark.asyncio
async def test_get_group(galene_api):
    with respx.mock:
        respx.get("https://localhost:8443/galene-api/v0/.groups/test-group").respond(
            json={"description": "Test Group", "public": True, "custom_field": "val"},
            headers={"ETag": '"abcd"'}
        )
        group, etag = await galene_api.groups.get_group("test-group")
        
        assert etag == '"abcd"'
        assert group.description == "Test Group"
        assert group.public is True
        assert group.model_extra["custom_field"] == "val"

@pytest.mark.asyncio
async def test_update_group(galene_api):
    with respx.mock:
        mock_put = respx.put("https://localhost:8443/galene-api/v0/.groups/test-group").respond(status_code=204)
        
        group = GroupDefinition(description="Updated", public=False)
        await galene_api.groups.update_group("test-group", group, etag='"abcd"')
        
        assert mock_put.called
        assert mock_put.calls[0].request.headers["If-Match"] == '"abcd"'

@pytest.mark.asyncio
async def test_list_users(galene_api):
    with respx.mock:
        respx.get("https://localhost:8443/galene-api/v0/.groups/test-group/.users/").respond(
            json=["user1", "user2"]
        )
        users = await galene_api.users.list_users("test-group")
        assert users == ["user1", "user2"]

@pytest.mark.asyncio
async def test_get_user(galene_api):
    with respx.mock:
        respx.get("https://localhost:8443/galene-api/v0/.groups/test-group/.users/test-user").respond(
            json={"permissions": ["present", "op"]}
        )
        user = await galene_api.users.get_user("test-group", "test-user")
        assert "op" in user.permissions
