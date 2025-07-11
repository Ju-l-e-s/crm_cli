from typing import List, Tuple, Type

from views.client_view import ClientsView
from views.contract_view import ContractsView
from views.event_view import EventsView
from views.user_view import UsersView


def get_menu_options(role: str) -> List[Tuple[str, Type[object]]]:
    """
    Get the list of menu options available for the given user role.

    Args:
        role: The role of the current user. Can be 'commercial', 'support', or 'gestion'.

    Returns:
        List[Tuple[str, Union[Type[object], None]]]: A list of (label, view_class) tuples.
            The view_class can be None for special actions like logout/quit.
    """
    options = [
        ("Clients", ClientsView),
        ("Contracts", ContractsView),
        ("Events", EventsView),
    ]
    if role == "gestion":
        options.append(("Collaborators", UsersView))
    options.append(("Log out", None))
    options.append(("Quit", None))
    return options
