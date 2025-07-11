from typing import Type

from sqlalchemy.orm import Session

from config.console import Console
from config.sentry_logging import capture_event
from controllers.repositories.client_repository import ClientRepository
from controllers.services.auth import get_current_user
from controllers.services.authorization import (
    get_client_owner_id,
    requires_ownership_or_role,
    requires_role,
)
from controllers.validators.validators import (
    validate_company,
    validate_email,
    validate_name,
    validate_phone,
)
from exceptions import CrmInvalidValue, CrmNotFoundError
from models.client import Client
from models.user import User
import views.client_view as client_view


class ClientController:
    """
    Controller for client management flows: list, add, edit, delete.
    """

    def __init__(self, session: Session, current_user: User, console: Console):
        """
        Initialize the ClientController.

        Args:
            session (Session): Database session.
            current_user (User): The currently authenticated user.
            console (Console): Console interface for I/O operations.
        """
        self.session = session
        self.current_user = current_user
        self.console = console
        self.repo = ClientRepository(session)
        self.view = client_view.ClientsView(console)

    def show_menu(self) -> None:
        """
        Display the clients menu and loop until 'Back' is chosen.
        """
        while True:
            choice = self.view.show_menu(self.current_user.role.value)
            if choice == "List clients":
                self.list_clients()
            elif choice == "List my clients":
                clients = self.list_by_commercial()
                self.view.display_client_table(clients, my_clients=True)
            elif choice == "Add client":
                self.add_client()
            elif choice == "Edit client":
                self.edit_client()
            elif choice == "Delete client":
                self.delete_client()
            elif choice == "Back":
                break

    def list_clients(self) -> None:
        """
        List clients: commercial sees own, others see all.
        """
        clients = self.repo.list_all()
        self.view.display_client_table(clients)

    @requires_role("commercial")
    def list_by_commercial(self) -> list[Type[Client]]:
        """
        Lists all clients from the current commercial.

        Returns:
            list[Type[Client]]: List of clients associated with the current commercial.
        """
        return self.repo.list_by_commercial(self.current_user.id)

    def add_client(self) -> None:
        """
        Prompt and create a new client, then display result or error.
        """
        try:
            data = self.view.prompt_new_client()
            client = self._create_client(**data)
            capture_event("Client created", level="info", client_id=client.id)
            self.view.show_success(f"Created client ID {client.id}")
        except CrmInvalidValue as e:
            capture_event("Client creation failed",
                          level="error", reason=str(e))
            self.view.show_error(str(e))

    @requires_role("commercial")
    def _create_client(self, fullname: str, email: str, phone: str, company: str) -> Client:
        """
        Creates a new client in the database and associates it with the current commercial.

        Args:
            fullname (str): The client's full name.
            email (str): The client's email.
            phone (str): The client's phone number.
            company (str): The client's company name.

        Returns:
            Client: The created client.

        Raises:
            CrmInvalidValue: If validation fails or email/phone already exists.
        """
        fullname = validate_name(fullname)
        email = validate_email(email)
        if self.repo.get_by_email(email):
            raise CrmInvalidValue("Email already exists.")
        phone = validate_phone(phone)
        if self.repo.get_by_phone(phone):
            raise CrmInvalidValue("Phone already exists.")
        company = validate_company(company)
        current = get_current_user(self.session)
        client = Client(fullname=fullname, email=email, phone=phone,
                        company=company, commercial_id=current.id)
        return self.repo.save(client)

    def edit_client(self) -> None:
        """
        Prompt and update an existing client, then display result or error.
        """
        try:
            client_id = self.view.prompt_client_id(edit=True)
            client = self.get_client_by_id(client_id)
            updates = self.view.prompt_edit_client(client)
            updated = self._update_client(client_id=client_id, **updates)
            capture_event("Client updated", level="info", client_id=updated.id)
            self.view.show_success(f"Updated client ID {updated.id}")
        except CrmInvalidValue as e:
            capture_event("Client update failed", level="error", reason=str(e))
            self.view.show_error(str(e))

    @requires_ownership_or_role(get_client_owner_id, 'gestion')
    def _update_client(self, client_id: int, fullname: str, email: str, phone: str, company: str) -> Client:
        """
        Updates a client's information and returns it.

        Args:
            client_id (int): The ID of the client to update.
            fullname (str): The new full name.
            email (str): The new email.
            phone (str): The new phone number.
            company (str): The new company name.

        Returns:
            Client: The updated client.

        Raises:
            CrmInvalidValue: If validation fails or email/phone already exists.
        """
        client = self.get_client_by_id(client_id)

        fullname = validate_name(fullname)
        email = validate_email(email)
        if self.repo.get_by_email(email) and not client.email == email:
            raise CrmInvalidValue("Email already exists.")
        phone = validate_phone(phone)
        if self.repo.get_by_phone(phone) and not client.phone == phone:
            raise CrmInvalidValue("Phone already exists.")
        company = validate_company(company)

        client.fullname = fullname
        client.email = email
        client.phone = phone
        client.company = company

        return self.repo.save(client)

    def delete_client(self) -> None:
        """
        Prompt and delete a client, then display result or error.
        """
        try:
            client_id = self.view.prompt_client_id(edit=False)
            if not self.get_client_by_id(client_id):
                raise CrmNotFoundError("Client")
            confirm = self.view.prompt_delete_confirmation(client_id)
            if not confirm:
                self.view.show_info("Operation cancelled.")
                return
            self._delete_client(client_id=client_id)
            capture_event("Client deleted", level="info", client_id=client_id)
            self.view.show_success(f"Client ID {client_id} has been deleted.")
        except CrmInvalidValue as e:
            capture_event("Client deletion failed",
                          level="error", reason=str(e))
            self.view.show_error("Please enter a valid client ID (number).")
        except CrmNotFoundError as e:
            capture_event("Client deletion failed",
                          level="info", reason=str(e))
            self.view.show_error(str(e))

    @requires_ownership_or_role(get_client_owner_id, 'gestion')
    def _delete_client(self, client_id: int) -> None:
        """
        Deletes the client with the given ID.

        Args:
            client_id (int): The ID of the client to delete.
        """
        client = self.get_client_by_id(client_id)
        self.repo.delete(client)

    def list_all_clients(self):
        """
        Return list of all clients.

        Returns:
            List of all Client objects.
        """
        return self.repo.list_all()

    def get_client_by_id(self, client_id: int) -> Client:
        """
        Retrieves a single client by ID or raises.

        Args:
            client_id (int): The ID of the client to retrieve.

        Returns:
            Client: The requested client.

        Raises:
            CrmNotFoundError: If no client with the given ID exists.
        """
        client = self.repo.get_by_id(client_id)
        if not client:
            raise CrmNotFoundError("Client")
        return client
