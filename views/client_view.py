from exceptions import CrmInvalidValue, CrmNotFoundError
from views.base import display_menu, display_error, display_success, create_table

from controllers.client_controller import ClientController


class ClientsView:
    def __init__(self, user, console, session):
        self.user = user
        self.console = console
        self.controller = ClientController(session)

    def show_menu(self):
        """
        Display the clients menu and handle user input.
        """
        while True:
            options = [
                ("List clients", self.list_clients),
                ("Add client", self.add_client) if self.user.role.value == "commercial" else None,
                ("Edit client", self.edit_client) if self.user.role.value in ("commercial", "gestion") else None,
                ("Back", lambda: "back"),
            ]
            valid_options = [opt for opt in options if opt]
            choice_idx = display_menu("Clients Menu", [label for label, _ in valid_options]) - 1
            _, action = valid_options[choice_idx]
            if action() == "back":
                break

    def list_clients(self):
        try:
            clients = self.controller.list_all_clients()
            table = create_table("All Clients", ["ID", "Name", "Email", "Phone", "Company"])
            for c in clients:
                table.add_row(str(c.id), c.fullname, c.email, c.phone, c.company)
            self.console.print(table)
        except CrmInvalidValue as e:
            display_error(str(e))

    def add_client(self):
        fullname = self.console.input("Full name: ")
        email = self.console.input("Email: ")
        phone = self.console.input("Phone: ")
        company = self.console.input("Company: ")
        try:
            client = self.controller.create_client(fullname, email, phone, company)
            display_success(f"Created client ID {client.id}")
        except CrmInvalidValue as e:
            display_error(str(e))

    def edit_client(self):
        client_id = self.console.input("Client ID to edit: ")
        if not client_id.isdigit():
            display_error("Invalid ID")
            return
        try:
            client = self.controller.get_client_by_id(int(client_id))
        except CrmNotFoundError as e:
            display_error(str(e))
            return
        self.console.print("[italic]Press Enter to keep the current value.[/italic]")
        fullname = self.console.input(f"New full name ([cyan]{client.fullname}[/cyan]): ").strip()
        email = self.console.input(f"New email ([cyan]{client.email}[/cyan]): ").strip()
        phone = self.console.input(f"New phone ([cyan]{client.phone}[/cyan]): ").strip()
        company = self.console.input(f"New company ([cyan]{client.company}[/cyan]): ").strip()
        update_data = {
            'fullname': fullname or client.fullname,
            'email':    email    or client.email,
            'phone':    phone    or client.phone,
            'company':  company  or client.company,
        }
        try:
            client = self.controller.update_client(int(client_id), **update_data)
            display_success(f"Updated client ID {client.id}")
        except CrmInvalidValue as e:
            display_error(str(e))