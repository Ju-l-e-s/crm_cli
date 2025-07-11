from typing import Any, Optional

from sqlalchemy.orm import Session

from config.sentry_logging import capture_event
from controllers.repositories.contract_repository import ContractRepository
from controllers.repositories.event_repository import EventRepository
from controllers.services.auth import get_current_user
from controllers.services.authorization import requires_role
from controllers.validators.validators import (
    validate_attendees,
    validate_event_dates,
    validate_event_name,
    validate_location,
)
from exceptions import (
    CrmForbiddenAccessError,
    CrmIntegrityError,
    CrmInvalidValue,
    CrmNotFoundError,
)
from models.event import Event
import views.event_view as event_view


class EventController:
    """
    Controller for event management flows: list, add, edit, assign support.
    """

    def __init__(self, session: Session, current_user: Any, console: Any) -> None:
        """
        Initialize the EventController.

        Args:
            session (Session): Database session.
            current_user: The currently authenticated user.
            console: Console interface for I/O operations.
        """
        self.session = session
        self.current_user = current_user
        self.console = console
        self.repo = EventRepository(session)
        self.contract_repo = ContractRepository(session)
        self.view = event_view.EventsView(console)

    def show_menu(self) -> None:
        """
        Display the events menu and loop until 'Back' is chosen.
        """
        while True:
            choice = self.view.show_menu(self.current_user.role.value)
            if choice == "List all events":
                self.list_all_events()
            elif choice == "List my events":
                self.list_my_events()
            elif choice == "List unassigned events":
                self.list_unassigned_events()
            elif choice == "Add event":
                self.add_event()
            elif choice == "Assign support":
                self.assign_support()
            elif choice == "Edit event":
                self.edit_event()
            elif choice == "Back":
                break

    def list_all_events(self) -> None:
        """
        List all events (all roles).
        """
        try:
            events = self.repo.list_all()
            self.view.display_event_table(events, title="All Events")
        except Exception as e:
            capture_event("Event list failed", level="error", reason=str(e))
            self.view.show_error(str(e))

    @requires_role("support")
    def list_my_events(self) -> None:
        """
        List events assigned to the current support user.
        """
        try:
            uid = self.current_user.id
            events = self.repo.list_by_support_contact(uid)
            self.view.display_event_table(events, title="My Events")
        except Exception as e:
            capture_event("My-events list failed",
                          level="error", reason=str(e))
            self.view.show_error(str(e))

    @requires_role("gestion")
    def list_unassigned_events(self) -> None:
        """
        List all events without a support contact (gestion only).
        """
        events = self.repo.list_without_support()
        self.view.display_event_table(events, title="Unassigned Events")


    @requires_role("commercial")
    def add_event(self) -> None:
        """
        Prompt and create a new event, then display result or error.
        """
        try:
            data = self.view.prompt_new_event()
            evt = self._create_event(**data)
            capture_event("Event created", level="info", event_id=evt.id)
            self.view.show_success(f"Created event ID {evt.id}")
        except (CrmInvalidValue, CrmNotFoundError) as e:
            capture_event("Event creation failed",
                          level="error", reason=str(e))
            self.view.show_error(str(e))

    @requires_role("commercial")
    def _create_event(
        self,
        contract_id: int,
        name: str,
        start_date: str,
        end_date: str,
        location: str,
        attendees: int,
        notes: Optional[str] = None
    ) -> Event:
        """
        Business logic to create an event under a signed contract.

        Args:
            contract_id: ID of the contract under which the event is created.
            name: Name of the event.
            start_date: Start date of the event.
            end_date: End date of the event.
            location: Location of the event.
            attendees: Number of attendees.
            notes: Optional notes about the event.

        Returns:
            Event: The created event.

        Raises:
            CrmNotFoundError: If the contract is not found.
            CrmInvalidValue: If the contract is not signed or not owned by the current user.
            CrmIntegrityError: If there's an error saving the event.
        """
        user = self.current_user

        # contract existence & ownership & signed
        contract = self.contract_repo.get_by_id(contract_id)
        if not contract:
            raise CrmNotFoundError("Contract")
        if not contract.is_signed:
            raise CrmInvalidValue("Cannot create event for unsigned contract.")
        if contract.commercial_id != user.id:
            raise CrmInvalidValue(
                "You can only create events for your own contracts.")

        # validate inputs
        name_ = validate_event_name(name)
        loc_ = validate_location(location)
        att_ = validate_attendees(attendees)
        start_dt, end_dt = validate_event_dates(start_date, end_date)

        event = Event(
            contract_id=contract_id,
            name=name_,
            start_date=start_dt,
            end_date=end_dt,
            location=loc_,
            attendees=att_,
            notes=notes,
        )
        try:
            return self.repo.save(event)
        except Exception as e:
            raise CrmIntegrityError(f"Could not create event: {e}") from e

    def edit_event(self) -> None:
        """
        Prompt and update an existing event, then display result or error.
        """
        try:
            event_id = self.view.prompt_event_id()
            event = self.get_event_by_id(event_id)
            data = self.view.prompt_edit_event(event)
            updated = self._update_event(event_id=event_id, **data)
            capture_event("Event updated", level="info", event_id=updated.id)
            self.view.show_success(f"Updated event ID {updated.id}")
        except (CrmInvalidValue, CrmNotFoundError, CrmForbiddenAccessError) as e:
            capture_event("Event update failed", level="error", reason=str(e))
            self.view.show_error(str(e))

    def _update_event(
        self,
        event_id: int,
        name: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[int] = None,
        notes: Optional[str] = None
    ) -> Event:
        """
        Business logic to update an existing event.
        Support may update only their own assigned events.
        Gestion may update any event.

        Args:
            event_id: ID of the event to update.
            name: New name for the event.
            start_date: New start date for the event.
            end_date: New end date for the event.
            location: New location for the event.
            attendees: New number of attendees.
            notes: New notes for the event.

        Returns:
            Event: The updated event.

        Raises:
            CrmNotFoundError: If the event is not found.
            CrmForbiddenAccessError: If the user doesn't have permission to update the event.
            CrmInvalidValue: If any of the provided values are invalid.
            CrmIntegrityError: If there's an error saving the event.
        """
        event = self.repo.get_by_id(event_id)
        if not event:
            raise CrmNotFoundError("Event")

        # --- specific authorizations support vs gestion  ---
        user = get_current_user(self.session)
        if user.role.value == "support":
            # support can only edit events assigned to them
            if event.support_contact_id != user.id:
                raise CrmForbiddenAccessError(
                    "You can only update events assigned to you.")
        elif user.role.value != "gestion":
            # other roles (commercial,…) are not authorized
            raise CrmForbiddenAccessError()

        # assign validated fields
        if name is not None:
            event.name = validate_event_name(name)
        if location is not None:
            event.location = validate_location(location)
        if attendees is not None:
            event.attendees = validate_attendees(attendees)
        if notes is not None:
            event.notes = notes
        if start_date is not None or end_date is not None:
            s, e = validate_event_dates(
                start_date or event.start_date, end_date or event.end_date)
            event.start_date, event.end_date = s, e

        try:
            return self.repo.save(event)
        except Exception as e:
            raise CrmIntegrityError(f"Could not update event: {e}") from e

    def get_event_by_id(self, event_id: int) -> Event:
        """
        Retrieve a single event by ID or raise if not found.

        Args:
            event_id: ID of the event to retrieve

        Returns:
            Event: The retrieved event

        Raises:
            CrmNotFoundError: If the event is not found.
        """
        event = self.repo.get_by_id(event_id)
        if not event:
            raise CrmNotFoundError("Event")
        return event

    def assign_support(self) -> None:
        """
        Prompt and assign a support contact to an event, then display result or error.
        """
        try:
            if not self.repo.list_without_support():
                self.view.show_info("All events are assigned.")
                return
            event_id, support_contact_id = self.view.prompt_assign_support()
            event = self._assign_support(event_id=event_id, support_contact_id=support_contact_id)
            capture_event("Support assigned to event",
                          level="info", event_id=event.id)
            self.view.show_success(
                f"Assigned support ID {support_contact_id} to event ID {event_id}")
        except (CrmInvalidValue, CrmNotFoundError) as e:
            capture_event("Assign support failed",
                          level="error", reason=str(e))
            self.view.show_error(str(e))

    @requires_role("gestion")
    def _assign_support(self, event_id: int, support_contact_id: int) -> Event:
        """
        Business logic to attach a support user to an event.

        Args:
            event_id: ID of the event to assign support to
            support_contact_id: ID of the support contact to assign

        Returns:
            Event: The updated event

        Raises:
            CrmNotFoundError: If the event or support user is not found.
            CrmInvalidValue: If the support user doesn't have the support role.
            CrmIntegrityError: If there's an error saving the event.
        """
        event = self.repo.get_by_id(event_id)
        if not event:
            raise CrmNotFoundError("Event")

        from controllers.repositories.user_repository import UserRepository
        user_repo = UserRepository(self.session)
        sup = user_repo.get_by_id(support_contact_id)
        if not sup:
            raise CrmNotFoundError("Support user")
        if sup.role.value != "support":
            raise CrmInvalidValue("User must have support role.")

        event.support_contact_id = support_contact_id
        try:
            return self.repo.save(event)
        except Exception as e:
            raise CrmIntegrityError(
                f"Could not assign support to event: {e}") from e
