import sys
from config.console import console

from views.base import display_success, display_info
from views.auth_view import prompt_login
from views.menu import run_main_menu


def authenticate():
    """Prompt the user to log in until credentials are valid and return the user object."""
    user = None
    while not user:
        user = prompt_login()
    return user


def main():
    display_success("Welcome to Epic Events CRM CLI")

    # Main loop: authenticate, then run menu until quit
    while True:
        user = authenticate()
        result = run_main_menu(user)
        if result == "quit":
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.clear()
        display_info("\nApplication interrupted by user. Goodbye!")
        sys.exit(0)
