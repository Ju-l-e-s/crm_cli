from exceptions import CrmInvalidValue, CrmNotFoundError
from decimal import Decimal
from views.base import display_menu, display_error, display_success, create_table, display_info

from controllers.contract_controller import ContractController


class ContractsView:
    def __init__(self, user, console, session):
        self.user = user
        self.console = console
        self.controller = ContractController(session)

    def show_menu(self):
        """
        Display the contracts menu and handle user input.
        """
        while True:
            options = [
                ("List all contracts", self.list_all),
                ("List my contracts",
                 self.list_mine) if self.user.role.value == "commercial" else None,
                ("Add contract", self.add_contract) if self.user.role.value == "gestion" else None,
                ("Edit contract", self.edit_contract) if self.user.role.value in (
                    "gestion", "commercial") else None,
                ("Back", lambda: "back"),
            ]
            valid_options = [opt for opt in options if opt]
            choice_idx = display_menu(
                "Contracts Menu", [label for label, _ in valid_options]) - 1
            label, action = valid_options[choice_idx]
            if action() == "back":
                break

    def list_all(self):
        try:
            ctrs = self.controller.list_all_contracts()
            if not ctrs:
                display_info("No contracts found.", clear=False)
                return

            table = create_table(
                "All Contracts", ["ID", "Client", "Total", "Remaining", "Signed", "End date"])
            for contract in ctrs:
                table.add_row(str(contract.id), str(contract.client_id), f"{contract.total_amount}", f"{contract.remaining_amount}", str(
                    contract.is_signed), str(contract.end_date.strftime("%Y-%m-%d")))
            self.console.print(table)
        except (CrmInvalidValue, CrmNotFoundError) as e:
            display_error(str(e))

    def list_mine(self):
        try:
            ctrs = self.controller.list_by_commercial()
            if not ctrs:
                display_info("You don't have any contracts.", clear=False)
                return

            table = create_table("My Contracts", ["ID", "Client", "Total"])
            for contract in ctrs:
                table.add_row(str(contract.id), str(
                    contract.client_id), f"{contract.total_amount}")
            self.console.print(table)
        except (CrmInvalidValue, CrmNotFoundError) as e:
            display_error(str(e))

    def add_contract(self):
        client_id = self.console.input("Client ID: ")
        amount = self.console.input("Total amount: ")
        is_signed = self.console.input("Signed? (y/n): ")
        end_date = self.console.input("End date (YYYY-MM-DD): ")
        try:
            contract = self.controller.create_contract(int(client_id), Decimal(
                amount), is_signed.lower().startswith('y'), end_date)
            display_success(f"Created contract ID {contract.id}")
        except (CrmInvalidValue, CrmNotFoundError) as e:
            display_error(str(e))

    def edit_contract(self):
        contract_id = self.console.input("Contract ID to edit: ")
        if not contract_id.isdigit():
            display_error("Invalid ID")
            return
        try:
            contract = self.controller.get_contract_by_id(int(contract_id))
        except CrmNotFoundError as e:
            display_error(str(e))
            return
        self.console.print("[italic]Press Enter to keep the current value.[/italic]")
        amount = self.console.input(f"New total amount ([cyan]{contract.total_amount}[/cyan]): ").strip()
        is_signed = self.console.input(f"Signed? ([cyan]{contract.is_signed}[/cyan], y/n): ").strip()
        remaining = self.console.input(f"Remaining amount ([cyan]{contract.remaining_amount}[/cyan]): ").strip()
        end_date = self.console.input(f"End date ([cyan]{contract.end_date}[/cyan]): ").strip()
        update_data = {
            'amount': Decimal(amount) if amount else contract.total_amount,
            'is_signed': (is_signed.lower().startswith('y')) if is_signed else contract.is_signed,
            'remaining': Decimal(remaining) if remaining else contract.remaining_amount,
            'end_date': end_date or str(contract.end_date.strftime("%Y-%m-%d")),
        }
        try:
            contract = self.controller.update_contract(
                int(contract_id), **update_data)
            display_success(f"Updated contract ID {contract.id}")
        except (CrmInvalidValue, CrmNotFoundError) as e:
            display_error(str(e))
