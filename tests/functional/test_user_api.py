import pytest
import httpx
from polyfactory.factories.pydantic_factory import ModelFactory
from api_models.user import UserCreate, UserRead, UserUpdate
from uuid import UUID

class UserCreateFactory(ModelFactory[UserCreate]):
    __model__ = UserCreate

@pytest.mark.asyncio
async def test_create_user(authenticated_test_client: httpx.AsyncClient, admin_user_id: str):
    user_data = UserCreateFactory.build(is_admin=False)
    response = await authenticated_test_client.post(
        "/users", 
        json=user_data.model_dump()
    )
    assert response.status_code == 201
    user = UserRead.model_validate(response.json())
    assert user.name == user_data.name
    assert not user.is_admin

@pytest.mark.asyncio
async def test_list_users(authenticated_test_client: httpx.AsyncClient, admin_user_id: str):
    response = await authenticated_test_client.get("/users")
    assert response.status_code == 200
    users = [UserRead.model_validate(u) for u in response.json()]
    assert any(u.is_admin for u in users) # At least the seeded admin user
    assert len(users) >= 1

@pytest.mark.asyncio
async def test_get_user(authenticated_test_client: httpx.AsyncClient, admin_user_id: str):
    response = await authenticated_test_client.get(f"/users/{admin_user_id}")
    assert response.status_code == 200
    user = UserRead.model_validate(response.json())
    assert user.id == UUID(admin_user_id)
    assert user.is_admin

@pytest.mark.asyncio
async def test_update_user(authenticated_test_client: httpx.AsyncClient, admin_user_id: str):
    # Create a non-admin user first
    new_user_data = UserCreateFactory.build(is_admin=False)
    create_response = await authenticated_test_client.post(
        "/users", 
        json=new_user_data.model_dump()
    )
    new_user_id = create_response.json()["id"]

    update_data = UserUpdate(name="Updated Name", is_admin=True)
    response = await authenticated_test_client.patch(
        f"/users/{new_user_id}", 
        json=update_data.model_dump(exclude_unset=True)
    )
    assert response.status_code == 200
    updated_user = UserRead.model_validate(response.json())
    assert updated_user.name == "Updated Name"
    assert updated_user.is_admin
