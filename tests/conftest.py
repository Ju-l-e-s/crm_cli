import re
import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import pexpect
from unittest.mock import MagicMock

from models.base import Base
from models.event import Event
from models.client import Client
from models.contract import Contract
from models.user_role import UserRole
from models.user import User


# Disable Sentry for the during the tests
@pytest.fixture(autouse=True, scope="session")
def _disable_sentry():
    os.environ["DISABLE_SENTRY"] = "1"


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


def make_console():
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
        str: The command to run the application
    """
    try:
        return os.environ.get("APP_CMD", "poetry run python main.py")
    except:
        return "python main.py"


APP_CMD = get_app_cmd()

# Functions for integration tests


def login(cli, email, pwd, fullname) -> None:
    """
    Helper for user login.

    Args:
        cli (pexpect.spawn): The CLI to interact with.
        email (str): The user's email.
        pwd (str): The user's password.
        fullname (str): The user's full name.
    """
    cli.expect("Email:")
    cli.sendline(email)
    cli.expect("Password:")
    cli.sendline(pwd)
    cli.expect(fr"Welcome {fullname}")


def nav_main(cli, label, role=None) -> None:
    """
    Navigation in the main menu.

    Args:
        cli (pexpect.spawn): The CLI to interact with.
        label (str): The label of the menu item to navigate to.
        role (str, optional): The role of the user. Defaults to None.
    """
    cli.expect("Your choice:")
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


def nav_submenu(cli, menu_text, option) -> None:
    """
    Navigation in the submenu.

    Args:
        cli (pexpect.spawn): The CLI to interact with.
        menu_text (str): The text of the menu item to navigate to.
        option (str): The option to select.
    """
    cli.expect(menu_text)
    cli.sendline(option)


def extract_id(cli: pexpect.spawn) -> int:
    """
    Get all numbers from the buffer and return the last one.

    Args:
        cli (pexpect.spawn): The CLI to interact with.

    Returns:
        int: The last number found in the buffer.
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
    """
    Create test users for integration tests.

    Args:
        session (Session): The database session.

    Returns:
        dict: A dictionary of test users.
    """
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
