from decimal import Decimal
from typing import Dict

from exceptions import CrmInvalidValue
from models.contract import Contract

from .base import (
    create_table,
    display_error,
    display_info,
    display_menu,
    display_success,
)


class ContractsView:
    """
    CLI view for contract management: prompts and displays only.


    Attributes:
        user: The current user instance.
        console: The console instance used for all output operations.
    """

    def __init__(self, user, console):
        """
        Initialize the ContractsView with user and console instances.

        Args:
            user: The current user instance.
            console: The console instance to use for output operations.
        """
        self.user = user
        self.console = console

    def show_menu(self, role: str) -> str:
        """
        Display the contracts menu and return the chosen action label.

        Args:
            role: Role of the current user ('commercial' or 'gestion').

        Returns:
            str: The label of the selected menu option.
        """
        options = ["List all contracts"]
        if role == "commercial":
            options.append("List my contracts")
            options.append("List unsigned contracts")
            options.append("List unpaid contracts")
        if role == "gestion":
            options.append("Add contract")
        if role in ("commercial", "gestion"):
            options.append("Edit contract")
        options.append("Back")

        choice = display_menu("Contracts Menu", options)
        return options[choice - 1]

    def display_contract_table(
        self,
        contracts: list[Contract],
        title: str = "Contracts"
    ) -> None:
        """
        Display a table of contracts.

        Args:
            contracts: List of Contract objects to display.
            title: Optional title for the table. Defaults to "Contracts".
        """
        if not contracts:
            msg = "No contracts found."
            display_info(msg, clear=False)
            return

        cols = [
            "ID",
            "Client",
            "Commercial",
            "Total",
            "Remaining",
            "Signed",
            "Created",
            "End date",
        ]
        table = create_table(title, cols)
        for contract in contracts:
            created = (
                contract.creation_date.strftime("%Y-%m-%d")
                if hasattr(contract, "creation_date") and contract.creation_date
                else "-"
            )
            commercial = getattr(contract, "commercial", None)
            commercial_name = (
                commercial.fullname
                if commercial and hasattr(commercial, "fullname")
                else str(getattr(contract, "commercial_id", "-"))
            )

            table.add_row(
                str(contract.id),
                contract.client.fullname
                if hasattr(contract, "client")
                else str(getattr(contract, "client_id", "-")),
                commercial_name,
                f"{contract.total_amount}",
                f"{contract.remaining_amount}",
                "Yes" if contract.is_signed else "No",
                created,
                contract.end_date.strftime("%Y-%m-%d")
                if hasattr(contract, "end_date") and contract.end_date
                else "-",
            )
        self.console.print(table)

    def prompt_new_contract(self) -> Dict[str, any]:
        """
        Prompt for new contract data.

        Returns:
            Dict containing the new contract's information:
                - client_id: ID of the client (int)
                - amount: Total amount (Decimal)
                - is_signed: Whether the contract is signed (bool)
                - end_date: End date of the contract (str)

        Raises:
            CrmInvalidValue: If client_id is not a positive integer or amount is not a number.
        """
        client_id = self.console.input("Client ID: ")
        if not client_id.isdigit():
            raise CrmInvalidValue("Client ID must be a positive integer.")

        amount_str = self.console.input("Total amount: ")
        try:
            amount = Decimal(amount_str)
        except:
            raise CrmInvalidValue("Total amount must be a number.")

        is_signed = self.console.input(
            "Signed? (y/n): ").lower().startswith("y")
        end_date = self.console.input("End date (YYYY-MM-DD): ")

        return {
            "client_id": int(client_id),
            "amount": amount,
            "is_signed": is_signed,
            "end_date": end_date,
        }

    def prompt_contract_id(self) -> int:
        """
        Prompt for a contract ID.

        Returns:
            int: The contract ID entered by the user.

        Raises:
            CrmInvalidValue: If the input is not a valid integer.
        """
        val = self.console.input("Contract ID to edit: ")
        if not val.isdigit():
            raise CrmInvalidValue("Invalid ID")
        return int(val)

    def prompt_edit_contract(self, contract: Contract) -> Dict[str, any]:
        """
        Prompt for updated contract information.

        Args:
            contract: The Contract object being edited.

        Returns:
            Dict containing the updated contract information with optional keys:
                - amount: New total amount (Decimal, optional)
                - remaining: New remaining amount (Decimal, optional)
                - is_signed: New signed status (bool, optional)
                - end_date: New end date (str, optional)
        """
        self.console.print(
            "[italic]Press Enter to keep the current value.[/italic]")

        amount = self.console.input(
            f"New total amount ([cyan]{contract.total_amount}[/cyan]): ").strip()
        remaining = self.console.input(
            f"New remaining amount ([cyan]{contract.remaining_amount}[/cyan]): ").strip()
        signed = self.console.input(
            f"Signed? ([cyan]{'Yes' if contract.is_signed else 'No'})[/cyan], y/n: ").strip()
        end_date = self.console.input(
            f"End date ([cyan]{contract.end_date.strftime('%Y-%m-%d')}[/cyan]): ").strip()

        data = {
            "amount": Decimal(amount) if amount else None,
            "remaining": Decimal(remaining) if remaining else None,
            "is_signed": signed.lower().startswith("y") if signed else None,
            "end_date": end_date if end_date else None,
        }
        return data

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
