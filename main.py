import sys

import sentry_sdk
from sqlalchemy.orm import Session

from config.console import console
from config.sentry_logging import init_sentry
from controllers.auth_controller import AuthController
from controllers.menu_controller import MenuController
from database.session import SessionLocal
from exceptions import CrmAuthenticationError
from views.base import display_error, display_info, display_success


def main() -> None:
    """
    Main entry point for the Epic Events CRM CLI application.

    Raises:
        CrmAuthenticationError: If there's an authentication-related error.
        Exception: For any other unexpected errors during execution.
    """
    init_sentry()
    session: Session = SessionLocal()

    display_success("Welcome to Epic Events CRM CLI")

    while True:
        try:
            # Authenticate user
            auth_ctrl = AuthController(session)
            user = auth_ctrl.authenticate()
            # Set user context for Sentry
            sentry_sdk.set_user({
                "email": user.email,
                "fullname": user.fullname,
                "role": user.role.value
            })

            # Run main menu
            menu_ctrl = MenuController(session)
            result = menu_ctrl.run_main_menu(user)

            if result == "quit":
                break
        except CrmAuthenticationError:
            display_error("Session expired. Please log in again.")
            continue

    session.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.clear()
        display_info("Application interrupted by user. Goodbye!")
        sys.exit()
