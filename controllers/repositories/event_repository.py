from typing import List, Optional, Type
from sqlalchemy.orm import Session
from models.event import Event


class EventRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, event: Event) -> Event:
        """
        Saves an event to the database.
        """
        self.session.add(event)
        self.session.commit()
        self.session.refresh(event)
        return event

    def get_by_id(self, event_id: int) -> Optional[Event]:
        """
        Retrieves an event by its ID.
        """
        return self.session.query(Event).filter(Event.id == event_id).first()

    def list_all(self) -> list[Type[Event]]:
        """
        Returns all events in the system.
        """
        return self.session.query(Event).all()

    def list_by_support_contact(self, support_contact_id: int) -> list[Type[Event]]:
        """
        Lists events assigned to a specific support contact.
        """
        return self.session.query(Event).filter(Event.support_contact_id == support_contact_id).all()

    def list_without_support(self) -> list[Type[Event]]:
        """
        Lists all events that have no support contact assigned.
        """
        return self.session.query(Event).filter(Event.support_contact_id.is_(None)).all()

    def list_by_contract(self, contract_id: int) -> list[Type[Event]]:
        """
        Lists all events for a specific contract.
        """
        return self.session.query(Event).filter(Event.contract_id == contract_id).all()