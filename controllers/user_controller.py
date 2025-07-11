from typing import List, Optional, Type

from sqlalchemy.orm import Session

from config.console import console
from config.sentry_logging import capture_event
from controllers.repositories.user_repository import UserRepository
from controllers.services.auth import generate_token
from controllers.services.authorization import requires_role
from controllers.services.token_cache import save_token
from controllers.validators.validators import (
    validate_email,
    validate_name,
    validate_password,
    validate_role,
)
from exceptions import CrmInvalidValue
from models.user import User
from views.user_view import UsersView


class UserController:
    """
    Controller orchestrating CLI flows for user management.

    This controller handles user-related operations including listing, adding, editing,
    deleting, and authenticating users. It enforces role-based access control and
    input validation.
    """

    def __init__(self, session: Session) -> None:
        """
        Initialize the UserController with a database session.

        Args:
            session: SQLAlchemy database session for database operations.
        """
        self.session = session
        self.repo = UserRepository(session)
        self.view = UsersView(console)

    def authenticate(self, email: str, password: str) -> User:
        """
        Authenticate a user and generate an authentication token.

        Args:
            email: The email address of the user to authenticate.
            password: The password to validate.

        Returns:
            User: The authenticated user object if successful.

        Raises:
            CrmInvalidValue: If authentication fails due to invalid credentials.
        """
        user = self.repo.get_by_email(email)
        if not user:
            raise CrmInvalidValue("User not found.")

        if not user.check_password(password):
            raise CrmInvalidValue("Wrong password.")

        token = generate_token(user)
        save_token(token)
        return user

    @requires_role("gestion")
    def show_menu(self) -> None:
        """
        Display and handle the user management menu.

        Shows a menu of available user management operations and processes
        user input to navigate between different functionalities.
        """
        while True:
            try:
                choice = self.view.show_menu()
                if choice == "List users":
                    self.list_users()
                elif choice == "Add user":
                    self.add_user()
                elif choice == "Edit user":
                    self.edit_user()
                elif choice == "Delete user":
                    self.delete_user()
                elif choice == "Back":
                    break
                else:
                    self.view.show_error(f"Unknown option: {choice}")

            except CrmInvalidValue as e:
                self.view.show_error(str(e))

    def list_users(self) -> None:
        """
        Display a table of all users in the system.

        Retrieves all users and displays them in a formatted table view.
        Requires 'gestion' role permissions.
        """
        try:
            users = self.list_all_users()
            self.view.display_user_table(users)
        except CrmInvalidValue as e:
            capture_event("User list failed", level="error", reason=str(e))
            self.view.show_error(str(e))

    @requires_role("gestion")
    def add_user(self) -> None:
        """
        Handle the user creation workflow.

        Prompts for user details, validates them, and creates a new user.
        Requires 'gestion' role permissions.
        """
        try:
            data = self.view.prompt_new_user()
            user = self.create_user(**data)
            self.view.show_success(f"Created user ID {user.id}")
            capture_event("User created", level="info", user_id=user.id)

        except CrmInvalidValue as e:
            capture_event(
                "User creation failed - Validation error",
                level="error",
                error=str(e)
            )
            self.view.show_error(str(e))

    @requires_role("gestion")
    def edit_user(self) -> None:
        """
        Handle the user editing workflow.

        Prompts for user ID and new details, validates them, and updates the user.
        Requires 'gestion' role permissions.
        """
        try:
            uid = self.view.prompt_user_id("User ID to edit")
            user = self.get_user_by_id(uid)
            if not user:
                raise CrmInvalidValue("User not found")

            data_to_update = self.view.prompt_edit_user(user)
            updated_user = self.update_user(uid, **data_to_update)

            self.view.show_success(f"Updated user ID {updated_user.id}")
            capture_event("User updated", level="info",
                          user_id=updated_user.id)

        except CrmInvalidValue as e:
            capture_event(
                "User update failed - Validation error",
                level="error",
                error=str(e)
            )
            self.view.show_error(str(e))

    @requires_role("gestion")
    def delete_user(self) -> None:
        """
        Handle the user deletion workflow.

        Prompts for user ID, confirms deletion, and removes the user.
        Requires 'gestion' role permissions.
        """
        try:
            uid = self.view.prompt_user_id("User ID to delete")
            confirm = self.view.prompt_delete_confirmation(uid)
            user = self.get_user_by_id(uid)

            if not confirm:
                self.view.show_info("Operation cancelled.")
                return

            self.delete_user_logic(user)

            capture_event("User deleted", level="info", user_id=uid)
            self.view.show_success(f"User ID {uid} has been deleted.")

        except CrmInvalidValue as e:
            capture_event(
                "User deletion failed - Validation error",
                level="error",
                error=str(e)
            )
            self.view.show_error("Please enter a valid user ID (number).")

    # --- Business Logic ---

    def create_user(self, fullname: str, email: str, role: str, password: str) -> User:
        """
        Create a new user with the provided details.

        Args:
            fullname: The full name of the user.
            email: The email address of the user (must be unique).
            role: The role of the user (e.g., 'gestion', 'commercial', 'support').
            password: The password for the user account.

        Returns:
            User: The newly created user object.

        Raises:
            CrmInvalidValue: If validation fails or email is already in use.
        """
        fullname = validate_name(fullname)
        email = validate_email(email)

        if self.repo.get_by_email(email):
            raise CrmInvalidValue("This email is already registered.")

        password = validate_password(password)
        role = validate_role(role)

        user = User(fullname=fullname, email=email, role=role)
        user.set_password(password)

        saved_user = self.repo.save(user)
        capture_event("User created", user_id=saved_user.id, level="info")
        return saved_user

    @requires_role("gestion")
    def list_all_users(self) -> List[Type[User]]:
        """
        Retrieve a list of all users in the system.

        Returns:
            List[User]: A list of all user objects.
        """
        return self.repo.list_all()

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Retrieve a user by their ID.

        Args:
            user_id: The ID of the user to retrieve.

        Returns:
            Optional[User]: The user object if found, None otherwise.
        """
        return self.repo.get_by_id(user_id)

    @requires_role("gestion")
    def update_user(
        self,
        user_id: int,
        fullname: str,
        email: str,
        role: str,
        password: Optional[str] = None
    ) -> User:
        """
        Update an existing user's details.

        Args:
            user_id: The ID of the user to update.
            fullname: The new full name for the user.
            email: The new email address for the user.
            role: The new role for the user.
            password: Optional new password for the user.

        Returns:
            User: The updated user object.

        Raises:
            CrmInvalidValue: If validation fails or the user cannot be found.
        """
        user = self.repo.get_by_id(user_id)

        fullname = validate_name(fullname)
        email = validate_email(email)
        if self.repo.get_by_email(email) and not user.email == email:
            raise CrmInvalidValue("This email is already registered.")
        role = validate_role(role)

        user.fullname = fullname
        user.email = email
        user.role = role

        if password:
            password = validate_password(password)
            user.set_password(password)

        return self.repo.save(user)

    @requires_role("gestion")
    def delete_user_logic(self, user: User) -> None:
        """
        Delete a user by their ID.

        Args:
            user: The user object to delete.
        """
        return self.repo.delete(user)
