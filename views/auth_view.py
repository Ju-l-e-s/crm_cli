from config.console import console
from views.base import display_error, display_info


def get_credentials():
    """
    Display the login form and return (email, password).
    """
    console.print("\n[bold]Login[/]\n")
    try:
        email = console.input("Email: ")
        password = console.input("Password: ", password=True)
        return email, password
    except UnicodeDecodeError:
        show_login_error("Invalid input")
        return get_credentials()


def show_login_success(user):
    """
    Display a welcome message after successful login.
    """
    display_info(f"\nWelcome, {user.fullname}!\n")


def show_login_error(message: str):
    """
    Display a specific login error message.
    """
    display_error(message)


def show_logout_success():
    """
    Display a logout confirmation message.
    """
    display_info("\nLogout successful\n")
