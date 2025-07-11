from typing import Dict

from exceptions import CrmInvalidValue

from views.base import (
    create_table,
    display_error,
    display_info,
    display_menu,
    display_success,
)


class UsersView:
    """CLI view for user management: prompts and displays.

    This class provides all the user interface components for user management,
    including displaying menus, forms, and user data in a tabular format.
    It handles all user interactions related to user operations.

    Attributes:
        console: The console instance used for all output operations.
    """

    def __init__(self, console):
        """Initialize the UsersView with a console instance.

        Args:
            console: The console instance to use for output operations.
        """
        self.console = console

    def show_menu(self) -> str:
        """
        Display the users menu and return the chosen action label.

        Returns:
            str: The label of the selected menu option. One of:
                - 'List users'
                - 'Add user'
                - 'Edit user'
                - 'Delete user'
                - 'Back'
        """
        options = [
            "List users",
            "Add user",
            "Edit user",
            "Delete user",
            "Back",
        ]
        choice = display_menu("Collaborators Menu", options)
        return options[choice-1]

    def display_user_table(self, users) -> None:
        """
        Display a table of users.

        Args:
            users: A list of User objects to display.
        """
        table = create_table("All Users", ["ID", "Name", "Email", "Role"])
        for user in users:
            table.add_row(
                str(user.id),
                user.fullname,
                user.email,
                user.role.value
            )
        self.console.print(table)

    def prompt_new_user(self) -> Dict[str, str]:
        """
        Prompt for new user data.

        Returns:
            Dict[str, str]: A dictionary containing the new user's information:
                - fullname: Full name of the user
                - email: Email address
                - role: User role (commercial/support/gestion)
                - password: User's password

        Raises:
            CrmInvalidValue: If passwords do not match.
        """
        name = self.console.input("Full name: ")
        email = self.console.input("Email: ")
        role = self.console.input("Role (commercial/support/gestion): ")
        password = self.console.input("Password: ", password=True)
        confirm = self.console.input("Confirm password: ", password=True)

        if password != confirm:
            raise CrmInvalidValue(
                "Passwords do not match. User creation aborted.")

        return {
            "fullname": name,
            "email": email,
            "role": role,
            "password": password
        }

    def prompt_user_id(self, message: str) -> int:
        """Prompt for a user ID.

        Args:
            message: The prompt message to display to the user.

        Returns:
            int: The user ID entered by the user.

        Raises:
            CrmInvalidValue: If the input is not a valid integer.
        """
        uid = self.console.input(message)

        if not uid.isdigit():
            raise CrmInvalidValue("Invalid ID")

        return int(uid)

    def prompt_edit_user(self, user) -> Dict[str, str]:
        """
        Prompt for updated user information.

        Args:
            user: The User object being edited.

        Returns:
            Dict[str, str]: A dictionary containing the updated user information:
                - fullname: Updated full name
                - email: Updated email
                - role: Updated role
                - password: New password (if changed, empty string otherwise)

        Raises:
            CrmInvalidValue: If passwords do not match.
        """
        self.console.print(
            "[italic]Press Enter to keep the current value.[/italic]")
        name = self.console.input(
            f"New full name ([cyan]{user.fullname}[/cyan]): ").strip() or user.fullname
        email = self.console.input(
            f"New email ([cyan]{user.email}[/cyan]): ").strip() or user.email
        role = self.console.input(
            f"New role ([cyan]{user.role.value}[/cyan]): ").strip() or user.role.value

        password = self.console.input(
            "New password (leave blank to keep current): ",
            password=True
        )

        if password:
            confirm = self.console.input(
                "Confirm new password: ",
                password=True
            )
            if password != confirm:
                raise CrmInvalidValue(
                    "Passwords do not match. User update aborted.")

        return {
            "fullname": name,
            "email": email,
            "role": role,
            "password": password
        }

    def prompt_delete_confirmation(self, user_id: int) -> bool:
        """
        Prompt for user deletion confirmation.

        Args:
            user_id: The ID of the user to be deleted.

        Returns:
            bool: True if the user confirms deletion, False otherwise.
        """
        answer = self.console.input(
            f"Are you sure you want to delete user ID {user_id}? (y/n): ")
        return answer.lower() == 'y'

    def show_success(self, message: str) -> None:
        """
        Display a success message.

        Args:
            message: The success message to display.
        """
        display_success(message)

    def show_error(self, message: str) -> None:
        """
        Display an error message.

        Args:
            message: The error message to display.
        """
        display_error(message)

    def show_info(self, message: str) -> None:
        """
        Display an informational message.

        Args:
            message: The info message to display.
        """
        display_info(message)
