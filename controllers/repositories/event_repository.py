from typing import Optional, Type

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.event import Event


class EventRepository:
    """Repository class for handling database operations for Event model."""

    def __init__(self, session: Session):
        """Initialize the EventRepository with a database session.

        Args:
            session (Session): SQLAlchemy database session.
        """
        self.session = session

    def save(self, event: Event) -> Event:
        """Save an event to the database.

        Args:
            event (Event): The Event object to save.

        Returns:
            Event: The saved Event object with updated attributes.

        Raises:
            Exception: If there is an error during database operations.
        """
        try:
            self.session.add(event)
            self.session.commit()
            self.session.refresh(event)
            return event
        except IntegrityError:
            self.session.rollback()
            raise

    def get_by_id(self, event_id: int) -> Optional[Event]:
        """Retrieve an event by its ID.

        Args:
            event_id (int): The ID of the event to retrieve.

        Returns:
            Optional[Event]: The Event object if found, None otherwise.
        """
        return self.session.query(Event).filter(Event.id == event_id).first()

    def list_all(self) -> list[Type[Event]]:
        """Retrieve all events from the database.

        Returns:
            list[Type[Event]]: A list of all Event objects.
        """
        return self.session.query(Event).all()

    def list_by_support_contact(self, support_contact_id: int) -> list[Type[Event]]:
        """Retrieve all events assigned to a specific support contact.

        Args:
            support_contact_id (int): The ID of the support contact.

        Returns:
            list[Type[Event]]: A list of Event objects assigned to the support contact.
        """
        return self.session.query(Event).filter(Event.support_contact_id == support_contact_id).all()

    def list_without_support(self) -> list[Type[Event]]:
        """Retrieve all events without an assigned support contact.

        Returns:
            list[Type[Event]]: A list of Event objects without a support contact.
        """
        return self.session.query(Event).filter(Event.support_contact_id.is_(None)).all()

    def list_by_contract(self, contract_id: int) -> list[Type[Event]]:
        """Retrieve all events associated with a specific contract.

        Args:
            contract_id (int): The ID of the contract.

        Returns:
            list[Type[Event]]: A list of Event objects for the specified contract.
        """
        return self.session.query(Event).filter(Event.contract_id == contract_id).all()
