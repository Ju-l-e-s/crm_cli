from getpass import getpass
from config.console import console
from rich.prompt import Prompt

from controllers.user_controller import UserController
from controllers.services.token_cache import delete_token as auth_logout
from exceptions import CrmInvalidValue
from database.session import SessionLocal
from views.base import display_error, display_info


def prompt_login():
    """
    Display the login form and return the connected user
    """
    session = SessionLocal()
    try:
        console.print("\n[bold]Login[/]")
        email = Prompt.ask("Email")
        password = getpass("Password: ")
        
        user_controller = UserController(session)
        user = user_controller.authenticate(email, password)
        return user
    except CrmInvalidValue as e:
        display_error(str(e))
        return None
    except Exception as e:
        display_error(str(e))
        return None
    finally:
        session.close()

def logout():
    """
    Logout the user
    """
    auth_logout()
    console.clear()
    display_info("\nLogout successful\n")