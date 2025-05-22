from models.user import User
from repositories.user_repository import UserRepository

def test_user_repository_get_by_email(session, seeded_user):
    user_repository = UserRepository(session)
    email = seeded_user.email
    user = user_repository.get_by_email(email)
    assert user is not None

def test_get_user_by_email_not_found(session):
    user_repository = UserRepository(session)
    user = user_repository.get_by_email("emailwhonotexists@epicenvents.com")
    assert user is None

def test_get_user_by_id(session, seeded_user):
    user_repository = UserRepository(session)
    user = user_repository.get_by_id(seeded_user.id)
    assert user is not None

def test_get_user_by_id_not_found(session):
    user_repository = UserRepository(session)
    user = user_repository.get_by_id(0)
    assert user is None

def test_save_user_returns_user(session, seeded_user):
    user_repository = UserRepository(session)
    user = user_repository.save(seeded_user)
    assert user is not None

def test_delete_user(session, seeded_user):
    user_repository = UserRepository(session)
    user = user_repository.get_by_email(seeded_user.email)
    user_repository.delete(user)
    user = user_repository.get_by_email(seeded_user.email)
    assert user is None

def test_list_all_users(session, seeded_user):
    user_repository = UserRepository(session)
    users = user_repository.list_all()
    assert len(users) == 1