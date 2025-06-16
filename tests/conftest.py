import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models.base import Base
from unittest.mock import MagicMock


from models.user import User
from models.user_role import UserRole
from models.client import Client
from models.contract import Contract
from models.event import Event


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture
def user_data():
    return {
        "fullname": "Jules Lac",
        "email": "jules@epicevents.com",
        "role": "gestion",
        "password": "Azertyuiop123"
    }

@pytest.fixture
def client_data(seeded_user_commercial):
    return {
        "fullname": "Kevin Casey",
        "email": "kevin@startup.io",
        "phone": "+678 123 456 78",
        "company_name": "Cool Startup LLC",
        "commercial_id": seeded_user_commercial.id
    }

@pytest.fixture
def seeded_user(session):
    user = User(
        fullname="Test User",
        email="test@email.com",
        role=UserRole.GESTION
    )
    user.set_password("CorrectPassword123")
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@pytest.fixture
def seeded_user_commercial(session):
    user = User(
        fullname="Test User",
        email="test2@email.com",
        role=UserRole.COMMERCIAL
    )
    user.set_password("CorrectPassword123")
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def _make_console():
    """Return a MagicMock console with input, print and clear methods."""
    console = MagicMock()
    console.input = MagicMock()
    console.print = MagicMock()
    console.clear = MagicMock()
    return console