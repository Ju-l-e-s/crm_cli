import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models.base import Base
from unittest.mock import MagicMock
import pexpect
import re


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


# Constants for integration tests
def get_app_cmd() -> str:
    """
    Get the application command to run the CLI.

    Returns:
        str: The command to run the application, either from environment variable
             or defaulting to 'poetry run python main.py' or 'python main.py'.
    """
    try:
        return os.environ.get("APP_CMD", "poetry run python main.py")
    except:
        return "python main.py"


APP_CMD = get_app_cmd()

# Functions for integration tests


def login(cli, email, pwd, fullname):
    """Helper for user login."""
    cli.expect("Email:")
    cli.sendline(email)
    cli.expect("Password:")
    cli.sendline(pwd)
    cli.expect(fr"Welcome {fullname}")


def nav_main(cli, label, role=None):
    """Navigation in the main menu."""
    cli.expect("Main Menu")
    if role == "gestion":
        menu_map = {
            "Clients": "1",
            "Contracts": "2",
            "Events": "3",
            "Collaborators": "4",
            "Log out": "5",
            "Quit": "6",
        }
    else:
        menu_map = {
            "Clients": "1",
            "Contracts": "2",
            "Events": "3",
            "Log out": "4",
            "Quit": "5",
        }
    cli.sendline(menu_map[label])


def nav_submenu(cli, menu_text, option):
    """Navigation in the submenu."""
    cli.expect(menu_text)
    cli.sendline(option)


def extract_id(cli: pexpect.spawn) -> int:
    """
    Get all numbers from the buffer and return the last one.
    """
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

    # Combine current buffers and strip ANSI
    text = ansi_escape.sub('', cli.before + cli.after)
    nums = re.findall(r"\d+", text)

    # If we still have no digits, wait for the next chunk that contains one
    if not nums:
        cli.expect(r"\d+")
        more_text = ansi_escape.sub('', cli.after)
        nums = re.findall(r"\d+", more_text)

    return int(nums[-1])


@pytest.fixture
def setup_test_users(session):
    """Create test users for integration tests."""
    # Commercial user
    commercial = User(
        fullname="Bart Simpson",
        email="bart@simpson.com",
        role=UserRole.COMMERCIAL
    )
    commercial.set_password("Pwd1234")

    # Gestion user
    gestion = User(
        fullname="Seymour Skinner",
        email="skinner@ecole.com",
        role=UserRole.GESTION
    )
    gestion.set_password("Pwd1234")

    # Support user
    support = User(
        fullname="Milhouse Van Houten",
        email="milhouse@simpson.com",
        role=UserRole.SUPPORT
    )
    support.set_password("Pwd1234")

    session.add_all([commercial, gestion, support])
    session.commit()

    return {
        "commercial": commercial,
        "gestion": gestion,
        "support": support
    }