from typing import Callable, Dict

from sqlalchemy.orm import Session

from config.console import console
from controllers.auth_controller import AuthController
from controllers.client_controller import ClientController
from controllers.contract_controller import ContractController
from controllers.event_controller import EventController
from controllers.user_controller import UserController
from models.user import User
from views.base import display_info, display_menu, display_success
from views.menu_view import get_menu_options


class MenuController:
    """
    Controller for managing the main menu and routing to other controllers.
    """

    def __init__(self, session: Session) -> None:
        """
        Initialize the MenuController.

        Args:
            session (Session): Database session for the application.
        """
        self.session = session
        self.console = console
        self.controller_map: Dict[str, Callable[[User], object]] = {
            "Clients": lambda user: ClientController(self.session, user, self.console),
            "Contracts": lambda user: ContractController(self.session, user, self.console),
            "Events": lambda user: EventController(self.session, user, self.console),
            "Collaborators": lambda user: UserController(self.session),
        }
        self.auth_controller = AuthController(self.session)

    def run_main_menu(self, user: User) -> str:
        """
        Display and handle the main menu navigation.

        Args:
            user (User): The currently authenticated user.

        Returns:
            str: 'logout' if user logs out, 'quit' if user quits the application.
        """
        while True:
            display_success(f"Welcome {user.fullname} ({user.role.value.capitalize()})")

            # Get options from menu_view
            menu_items = get_menu_options(user.role.value)
            options = [label for label, _ in menu_items]

            # Display menu and get selection
            choice = display_menu("Main Menu", options)
            selected_label = options[choice - 1]

            # Execute selected action
            if selected_label == "Log out":
                self.auth_controller.logout_flow()
                return "logout"
            elif selected_label == "Quit":
                display_info("Exiting. Goodbye!")
                return "quit"
            else:
                self.console.clear()
                self.controller_map[selected_label](user).show_menu()
