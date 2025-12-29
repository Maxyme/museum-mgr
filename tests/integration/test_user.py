import pytest
from orm import user as user_repo
from tests.factories import UserCreateFactory


@pytest.mark.asyncio
async def test_user_crud(db_session):
    data = UserCreateFactory.build()
    # create a new user
    created_user = await user_repo.create_user(db_session, data)
    await db_session.commit()

    fetched_user = await user_repo.get_user(db_session, created_user.id)
    assert fetched_user == created_user

    # Check get all users
    users = await user_repo.list_users(db_session)
    assert len(users) == 1

