from views.base import create_table
from exceptions import CrmInvalidValue, CrmNotFoundError
from views.base import display_menu, display_error, display_success

from controllers.user_controller import UserController


class UsersView:
    def __init__(self, user, console, session):
        self.user = user
        self.console = console
        self.controller = UserController(session)

    def show_menu(self):
        """
        Display the users menu and handle user input. Gestion only.
        """
        while True:
            options = [
                ("List users", self.list_users),
                ("Add user", self.add_user) if self.user.role.value == "gestion" else None,
                ("Edit user", self.edit_user) if self.user.role.value == "gestion" else None,
                ("Back", lambda: "back"),
            ]
            valid_options = [opt for opt in options if opt]
            choice_idx = display_menu("Collaborators Menu", [label for label, _ in valid_options]) - 1
            _, action = valid_options[choice_idx]
            if action() == "back":
                break

    def list_users(self):
        try:
            users = self.controller.list_all_users()
            table = create_table("All Users", ["ID", "Name", "Email", "Role"])
            for u in users:
                table.add_row(str(u.id), u.fullname, u.email, u.role.value)
            self.console.print(table)
        except CrmInvalidValue as e:
            display_error(str(e))

    def add_user(self):
        fullname = self.console.input("Full name: ")
        email = self.console.input("Email: ")
        role = self.console.input("Role (commercial/support/gestion): ")
        password = self.console.input("Password: ")
        try:
            u = self.controller.create_user(fullname, email, role, password)
            display_success(f"Created user ID {u.id}")
        except CrmInvalidValue as e:
            display_error(str(e))

    def edit_user(self):
        uid = self.console.input("User ID to edit: ")
        if not uid.isdigit():
            display_error("Invalid ID", clear=False)
            return
        try:
            user = self.controller.get_user_by_id(int(uid))
        except CrmNotFoundError as e:
            display_error(str(e))
            return
        console = self.console
        console.print("[italic]Press Enter to keep the current value.[/italic]")
        name = console.input(f"New name ([cyan]{user.fullname}[/cyan]): ").strip()
        email = console.input(f"New email ([cyan]{user.email}[/cyan]): ").strip()
        role = console.input(f"New role ([cyan]{user.role.value}[/cyan]): ").strip()
        update_data = {
            'fullname': name or user.fullname,
            'email':    email or user.email,
            'role':     role or user.role.value,
        }
        try:
            u = self.controller.update_user(int(uid), **update_data)
            display_success(f"Updated user ID {u.id}")
        except CrmInvalidValue as e:
            display_error(str(e))