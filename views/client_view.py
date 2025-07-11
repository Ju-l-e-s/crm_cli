from typing import Dict, List, Optional

from config.console import console
from exceptions import CrmInvalidValue
from models.client import Client

from .base import create_table, display_error, display_info, display_menu, display_success


class ClientsView:
    """
    CLI view for client management: prompts and displays only.
    """

    def __init__(self, console):
        """
        Initialize the ClientsView with a console instance.

        Args:
            console: The console instance to use for output operations.
        """
        self.console = console

    def show_menu(self, role: str) -> str:
        """
        Display the clients menu and return the chosen action label.

        Args:
            role (str): The role of the current user (e.g., 'commercial', 'gestion').

        Returns:
            str: The label of the selected menu option.

        Note:
            The available options vary based on the user's role.
        """
        options = ["List clients"]
        if role == "commercial":
            options.append("List my clients")
            options.append("Add client")
        if role in ("commercial", "gestion"):
            options.extend(["Edit client", "Delete client"])
        options.append("Back")

        choice = display_menu("Clients Menu", options)
        return options[choice - 1]

    def display_client_table(self, clients: List[Client], my_clients: bool = False) -> None:
        """
        Display a table of clients.

        Args:
            clients: List of Client objects to display.
            my_clients: If True, indicates these are the current user's clients.
                       Affects the table title.
        """
        if not clients:
            msg = "No clients found."
            display_info(msg, clear=False)
            return

        cols = [
            "ID",
            "Name",
            "Email",
            "Phone",
            "Company",
            "Created",
            "Last contact",
            "Commercial",
        ]
        title = f"{'My' if my_clients else 'All'} Clients"
        table = create_table(title, cols)

        for client in clients:
            created = client.created_at.strftime("%Y-%m-%d")
            updated = client.updated_at.strftime("%Y-%m-%d")
            commercial = getattr(client, "commercial", None)
            commercial_name = commercial.fullname if commercial else "-"

            table.add_row(
                str(client.id),
                client.fullname,
                client.email,
                client.phone,
                client.company,
                created,
                updated,
                commercial_name,
            )
        self.console.print(table)

    def prompt_new_client(self) -> Dict[str, str]:
        """
        Prompt for new client data.

        Returns:
            Dict[str, str]: A dictionary containing the new client's information:
                - fullname: Client's full name
                - email: Client's email address
                - phone: Client's phone number
                - company: Client's company name
        """
        name = self.console.input("Full name: ")
        email = self.console.input("Email: ")
        phone = self.console.input("Phone: ")
        company = self.console.input("Company: ")
        return {
            "fullname": name,
            "email": email,
            "phone": phone,
            "company": company
        }

    def prompt_client_id(self, edit: bool = True) -> int:
        """
        Prompt for a client ID.

        Args:
            edit: If True, the ID is for editing; if False, for deletion.

        Returns:
            int: The client ID entered by the user.

        Raises:
            CrmInvalidValue: If the input is not a valid integer.
        """
        action = "edit" if edit else "delete"
        val = self.console.input(f"Client ID to {action}: ")
        if not val.isdigit():
            raise CrmInvalidValue("Invalid ID")
        return int(val)

    def prompt_edit_client(self, client: Client) -> Dict[str, str]:
        """
        Prompt for updated client information.

        Args:
            client: The Client object being edited.

        Returns:
            Dict[str, str]: A dictionary containing the updated client information.
        """
        self.console.print(
            "[italic]Press Enter to keep the current value.[/italic]")
        fullname = self.console.input(
            f"New full name ([cyan]{client.fullname}[/cyan]): ").strip() or client.fullname
        email = self.console.input(
            f"New email ([cyan]{client.email}[/cyan]): ").strip() or client.email
        phone = self.console.input(
            f"New phone ([cyan]{client.phone}[/cyan]): ").strip() or client.phone
        company = self.console.input(
            f"New company ([cyan]{client.company}[/cyan]): ").strip() or client.company
        return {
            "fullname": fullname,
            "email": email,
            "phone": phone,
            "company": company
        }

    def prompt_delete_confirmation(self, client_id: int) -> bool:
        """
        Prompt for confirmation before deleting a client.

        Args:
            client_id: The ID of the client to be deleted.

        Returns:
            bool: True if the user confirms deletion, False otherwise.
        """
        ans = self.console.input(
            f"Are you sure you want to delete client ID {client_id}? (y/n): ")
        return ans.lower() == 'y'

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
