import pytest
from orm import user as user_repo
from tests.factories import UserCreateFactory

@pytest.mark.asyncio
async def test_get_user(db_session):
    data = UserCreateFactory.build()
    created_user = await user_repo.create_user(db_session, data)
    await db_session.commit()

    fetched_user = await user_repo.get_user(db_session, created_user.id)
    
    assert fetched_user is not None
    assert fetched_user.id == created_user.id
    assert fetched_user.email == data.email
