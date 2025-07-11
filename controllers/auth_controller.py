from typing import Optional

from sqlalchemy.orm import Session

from controllers.user_controller import UserController
from controllers.services.token_cache import delete_token
from models.user import User
from views.auth_view import get_credentials, show_login_error, show_login_success, show_logout_success
from exceptions import CrmInvalidValue


class AuthController:
    """
    Controller that manages authentication logic and delegates to UserController.
    """
    def __init__(self, session: Session):
        self.session = session
        self.user_controller = UserController(session)

    def authenticate(self) -> User:
        """
        Prompt the user to log in until credentials are valid, return the user.

        Returns:
            User: The authenticated user
        """
        user = None
        while not user:
            user = self.login_flow()
        return user

    def login_flow(self) -> Optional[User]:
        """
        Handle login flow: show form, authenticate via UserController, handle responses.

        Returns:
            Optional[User]: The authenticated user or None
        """
        email, password = get_credentials()
        try:
            user = self.user_controller.authenticate(email, password)
            show_login_success(user)
            return user
        except CrmInvalidValue as e:
            show_login_error(str(e))
            return None

    def logout_flow(self):
        """
        Handle logout: clear token and show confirmation.
        """

        delete_token()
        show_logout_success()