from config.console import console
from views.base import display_menu, display_success, display_error, display_info
from views.client_view import ClientsView
from views.contract_view import ContractsView
from views.event_view import EventsView
from views.user_view import UsersView
from views.auth_view import logout
from database.session import SessionLocal
from exceptions import CrmAuthenticationError


def get_menu_options(role: str):
    """Return the list of (label, view_class or None) tuples for the given role."""
    options = [
        ("Clients", ClientsView),
        ("Contracts", ContractsView),
        ("Events", EventsView),
    ]
    if role == "gestion":
        options.append(("Collaborators", UsersView))
    # special actions
    options.append(("Log out", None))
    options.append(("Quit", None))
    return options


def run_main_menu(user):
    """Run the main menu loop for the given authenticated user.

    Returns:
        str: "logout" if user chose to log out, "quit" if application should exit.
    """
    while True:
        console.clear()
        display_success(f"Welcome {user.fullname} ([yellow]{user.role.value.capitalize()}[/])")

        menu_options = get_menu_options(user.role.value)
        choice_idx = display_menu("Main Menu", [label for label, _ in menu_options]) - 1
        label, view_class = menu_options[choice_idx]

        if view_class is None:
            # Special actions
            if label == "Log out":
                logout()
                return "logout"
            if label == "Quit":
                display_info("Exiting. Goodbye!")
                return "quit"

        # Regular view selected
        session = SessionLocal()
        try:
            console.clear()
            view_class(user, console, session=session).show_menu()
        except CrmAuthenticationError:
            display_error("Session expired. Please log in again.")
            return "logout"
        finally:
            session.close()