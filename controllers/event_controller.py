from typing import List, Type
from sqlalchemy.orm import Session
from datetime import datetime

from controllers.services.auth import get_current_user
from controllers.services.authorization import requires_role, requires_ownership_or_role, get_event_owner_id
from exceptions import CrmInvalidValue, CrmNotFoundError, CrmIntegrityError
from models.event import Event
from models.contract import Contract
from controllers.repositories.event_repository import EventRepository
from controllers.repositories.contract_repository import ContractRepository
from controllers.validators.validators import validate_event_name, validate_location, validate_attendees, validate_event_dates


class EventController:
    def __init__(self, session: Session):
        self.session = session

    @requires_role("commercial")
    def create_event(self, contract_id: int, name: str, start_date: str, end_date: str,
                     location: str, attendees: int, notes: str = None) -> Event:
        """
        Creates a new event for a signed contract owned by the current commercial.

        :param contract_id: ID of the contract for the event.
        :param name: Name of the event.
        :param start_date: Start date and time (YYYY-MM-DD HH:MM).
        :param end_date: End date and time (YYYY-MM-DD HH:MM).
        :param location: Location of the event.
        :param attendees: Number of attendees.
        :param notes: Optional notes about the event.
        :return: The created event.
        """
        # Get current user
        user = get_current_user(self.session)

        # Check if contract exists and is signed
        contract_repo = ContractRepository(self.session)
        contract = contract_repo.get_by_id(contract_id)
        if not contract:
            raise CrmNotFoundError("Contract")

        if not contract.is_signed:
            raise CrmInvalidValue("Cannot create event for unsigned contract.")

        # Check if user owns the contract
        if contract.commercial_id != user.id:
            raise CrmInvalidValue("You can only create events for your own contracts.")

        # Input validation
        event_name = validate_event_name(name)
        event_location = validate_location(location)
        event_attendees = validate_attendees(attendees)
        start_dt, end_dt = validate_event_dates(start_date, end_date)

        event = Event(
            name=event_name,
            start_date=start_dt,
            end_date=end_dt,
            location=event_location,
            attendees=event_attendees,
            notes=notes,
            contract_id=contract_id
        )

        try:
            return EventRepository(self.session).save(event)
        except Exception as e:
            raise CrmIntegrityError(f"Could not create event: {e}") from e

    def list_all_events(self) -> List[Type[Event]]:
        """
        Returns all events in the system (read-only access for all users).
        """
        return EventRepository(self.session).list_all()

    @requires_role("support")
    def list_my_events(self) -> List[Type[Event]]:
        """
        Lists events assigned to the current support user.
        """
        user = get_current_user(self.session)
        return EventRepository(self.session).list_by_support_contact(user.id)

    @requires_role("gestion")
    def list_events_without_support(self) -> List[Type[Event]]:
        """
        Lists all events that have no support contact assigned (gestion only).
        """
        return EventRepository(self.session).list_without_support()

    def get_event_by_id(self, event_id: int) -> Event:
        """
        Retrieves an event by its ID.
        :raises CrmInvalidValue: if not found.
        """
        event = EventRepository(self.session).get_by_id(event_id)
        if not event:
            raise CrmNotFoundError("Event")
        return event

    def get_contract_events(self, contract_id: int) -> List[Event]:
        """
        Lists all events for a specific contract.
        """
        return EventRepository(self.session).list_by_contract(contract_id)

    @requires_role("gestion")
    def assign_support_to_event(self, event_id: int, support_contact_id: int) -> Event:
        """
        Assigns a support contact to an event (gestion only).

        :param event_id: ID of the event.
        :param support_contact_id: ID of the support user to assign.
        :return: The updated event.
        """
        repo = EventRepository(self.session)
        event = repo.get_by_id(event_id)
        if not event:
            raise CrmNotFoundError("Event")

        # Validate that the support contact exists and has support role
        from controllers.repositories.user_repository import UserRepository
        user_repo = UserRepository(self.session)
        support_user = user_repo.get_by_id(support_contact_id)
        if not support_user:
            raise CrmNotFoundError("Support user")
        if support_user.role.value != "support":
            raise CrmInvalidValue("User must have support role.")

        event.support_contact_id = support_contact_id

        try:
            return repo.save(event)
        except Exception as e:
            raise CrmIntegrityError(f"Could not assign support to event: {e}") from e

    @requires_ownership_or_role(get_event_owner_id, "gestion")
    def update_event(self, event_id: int, name: str = None, start_date: str = None,
                     end_date: str = None, location: str = None, attendees: int = None,
                     notes: str = None) -> Event:
        """
        Updates an event. Support users can only update events assigned to them.
        Gestion can update any event.

        :param event_id: ID of the event.
        :param name: New name (optional).
        :param start_date: New start date (optional).
        :param end_date: New end date (optional).
        :param location: New location (optional).
        :param attendees: New number of attendees (optional).
        :param notes: New notes (optional).
        :return: The updated event.
        """
        user = get_current_user(self.session)
        repo = EventRepository(self.session)
        event = repo.get_by_id(event_id)
        if not event:
            raise CrmNotFoundError("Event")

        if self.controller.get_event_by_id(event_id).support_contact_id != user.id and user.role.value != "gestion":
            raise CrmInvalidValue("You can only update events assigned to you.")


        # Validate and assign values
        if name is not None:
            event.name = validate_event_name(name)
        if location is not None:
            event.location = validate_location(location)
        if attendees is not None:
            event.attendees = validate_attendees(attendees)
        if notes is not None:
            event.notes = notes
        if start_date is not None or end_date is not None:
            current_start = event.start_date if start_date is None else None
            current_end = event.end_date if end_date is None else None
            start_dt, end_dt = validate_event_dates(start_date or current_start, end_date or current_end)
            event.start_date = start_dt
            event.end_date = end_dt

        try:
            return repo.save(event)
        except Exception as e:
            raise CrmIntegrityError(f"Could not update event: {e}") from e