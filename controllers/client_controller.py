from typing import Type
from sqlalchemy.orm import Session

from controllers.services.auth import get_current_user
from controllers.services.authorization import (
    requires_role,
    requires_ownership_or_role,
    get_client_owner_id
)
from exceptions import CrmInvalidValue
from models.client import Client
from controllers.repositories.client_repository import ClientRepository
from controllers.validators.user_validators import validate_name, validate_email
from controllers.validators.client_validators import validate_phone, validate_company


class ClientController:
    def __init__(self, session: Session):
        self.session = session

    @requires_role("commercial")
    def create_client(self, fullname: str, email: str, phone: str, company: str) -> Client:
        """
        Creates a new client in the database.

        :param fullname: The client's full name.
        :param email: The client's email address.
        :param phone: The client's phone.
        :param company: The client's company.
        :return: The created client.

        """
        fullname = validate_name(fullname)
        email = validate_email(email)
        phone = validate_phone(phone)
        company = validate_company(company)

        client = Client(fullname=fullname, email=email, phone=phone, company=company)

        try:
            return ClientRepository(self.session).save(client)
        except Exception as e:
            raise CrmInvalidValue(f"Could not create client: {e}") from e


    def list_all_clients(self) -> list[Type[Client]]:
        """
        Lists all clients.
        """

        return ClientRepository(self.session).list_all()

    @requires_role("commercial")
    def list_by_commercial(self) -> list[Type[Client]]:
        """
        Lists all clients from a commercial.
        """
        user = get_current_user(self.session)
        return ClientRepository(self.session).list_by_commercial(user.id)

    def get_client_by_id(self, client_id: int) -> Client:
        """
        Retrieves a single client by ID.
        :raises CrmInvalidValue: If client does not exist.
        """
        client = ClientRepository(self.session).get_by_id(client_id)
        if not client:
            raise CrmInvalidValue("User not found.")
        return client

    @requires_ownership_or_role(get_client_owner_id,'gestion')
    def update_client(self, client_id: int, fullname: str, email: str, phone: str, company: str) -> Client:
        """
        Updates a client's information.
        """
        client = ClientRepository(self.session).get_by_id(client_id)
        if not client:
            raise CrmInvalidValue("User not found.")

        fullname = validate_name(fullname)
        email = validate_email(email)
        phone = validate_phone(phone)
        company = validate_company(company)

        client.fullname = fullname
        client.email = email
        client.phone = phone
        client.company = company


        try:
            return ClientRepository(self.session).save(client)
        except Exception as e:
            raise CrmInvalidValue(f"Could not update client: {e}") from e