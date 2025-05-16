import pytest
from user_controller import UserController
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
    with pytest.raises(ValueError) as excinfo:
        controller.create_user(
            fullname="RandomUser Two",
            email="duplicate@example.com",
            role="gestion",
            password="AnotherPass123"
        )
    assert "Could not create user" in str(excinfo.value)