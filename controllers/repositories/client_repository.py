from typing import Type

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.client import Client


class ClientRepository:
    """Repository class for handling database operations for Client model."""

    def __init__(self, session: Session):
        """Initialize the ClientRepository with a database session.

        Args:
            session (Session): SQLAlchemy database session.
        """
        self.session = session

    def get_by_email(self, email: str) -> Client | None:
        """Retrieve a client by their email address.

        Args:
            email (str): The email address of the client to retrieve.

        Returns:
            Client | None: The Client object if found, None otherwise.
        """
        return self.session.query(Client).filter_by(email=email).first()

    def get_by_id(self, client_id: int) -> Client | None:
        """Retrieve a client by their ID.

        Args:
            client_id (int): The ID of the client to retrieve.

        Returns:
            Client | None: The Client object if found, None otherwise.
        """
        return self.session.query(Client).filter_by(id=client_id).first()

    def get_by_phone(self, phone: str) -> Client | None:
        """Retrieve a client by their phone number.

        Args:
            phone (str): The phone number of the client to retrieve.

        Returns:
            Client | None: The Client object if found, None otherwise.
        """
        return self.session.query(Client).filter_by(phone=phone).first()

    def save(self, client: Client) -> Client:
        """Save a client to the database.

        Args:
            client (Client): The Client object to save.

        Returns:
            Client: The saved Client object with updated attributes.

        Raises:
            Exception: If there is an error during database operations.
        """
        try:
            self.session.add(client)
            self.session.commit()
            self.session.refresh(client)
            return client
        except IntegrityError:
            self.session.rollback()
            raise

    def delete(self, client: Client) -> None:
        """Delete a client from the database.

        Args:
            client (Client): The Client object to delete.

        Raises:
            Exception: If there is an error during database operations.
        """
        try:
            self.session.delete(client)
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise

    def list_all(self) -> list[Type[Client]]:
        """Retrieve all clients from the database.

        Returns:
            list[Type[Client]]: A list of all Client objects.
        """
        return self.session.query(Client).all()

    def list_by_commercial(self, user_id: int) -> list[Type[Client]]:
        """Retrieve all clients assigned to a specific commercial user.

        Args:
            user_id (int): The ID of the commercial user.

        Returns:
            list[Type[Client]]: A list of Client objects assigned to the specified commercial.
        """
        return self.session.query(Client).filter_by(commercial_id=user_id).all()
