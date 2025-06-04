import pytest
from controllers.user_controller import UserController
from exceptions import CrmInvalidValue
from tests.conftest import session

def test_create_valid_user(session,user_data):
    controller = UserController(session)
    user = controller.create_user(**user_data)
    assert user.id is not None
    assert user.fullname == user_data["fullname"]
    assert user.email == user_data["email"]
    assert user.role.value == user_data["role"]
    assert user.check_password(user_data["password"])

def test_create_user_duplicate_email(session):
    controller = UserController(session)
    controller.create_user(
        fullname="RandomUser One",
        email="duplicate@example.com",
        role="support",
        password="ValidPass123"
    )
    with pytest.raises(CrmInvalidValue) as excinfo:
        controller.create_user(
            fullname="RandomUser Two",
            email="duplicate@example.com",
            role="gestion",
            password="AnotherPass123"
        )
    assert "Could not create user" in str(excinfo.value)

def test_authenticate_success(session, seeded_user):
    controller = UserController(session)
    user = controller.authenticate("test@email.com", "CorrectPassword123")
    assert user.email == "test@email.com"

def test_authenticate_wrong_password(session, seeded_user):
    controller = UserController(session)
    with pytest.raises(CrmInvalidValue) as excinfo:
        controller.authenticate("test@email.com", "WrongPassword123")
    assert "Wrong password" in str(excinfo.value)

def test_authenticate_user_not_found(session):
    controller = UserController(session)
    with pytest.raises(CrmInvalidValue) as excinfo:
        controller.authenticate("unknown@email.com", "AnyPass123")
    assert "User not found" in str(excinfo.value)

def test_list_all_users(session, seeded_user):
    controller = UserController(session)

    users = controller.list_all_users()

    assert isinstance(users, list)
    assert any(user.id == seeded_user.id for user in users)


def test_update_user_success(session, seeded_user):
    controller = UserController(session)

    updated = controller.update_user(
        user_id=seeded_user.id,
        fullname="Updated Name",
        email="updated@email.com",
        role="support"
    )

    assert updated.id == seeded_user.id
    assert updated.fullname == "Updated Name"
    assert updated.email == "updated@email.com"
    assert updated.role.value == "support"


def test_update_user_not_found(session):
    controller = UserController(session)

    with pytest.raises(CrmInvalidValue, match="User not found"):
        controller.update_user(
            user_id=999,
            fullname="Any Name",
            email="email@nowhere.com",
            role="gestion"
        )