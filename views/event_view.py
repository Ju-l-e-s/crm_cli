from typing import Dict, Optional, Tuple, Any, List

from exceptions import CrmInvalidValue

from .base import (
    create_table,
    display_error,
    display_info,
    display_menu,
    display_success,
)


class EventsView:
    """
    CLI view for event management: menus, prompts, and displays only.

   

    Attributes:
        console: The console instance used for all output operations.
    """

    def __init__(self, console):
        """Initialize the EventsView with a console instance.

        Args:
            console: The console instance to use for output operations.
        """
        self.console = console

    def show_menu(self, role: str) -> str:
        """Display the events menu and return the chosen action label.

        Args:
            role: The role of the current user which determines available options.
                Can be 'support', 'gestion', 'commercial', or other roles.

        Returns:
            str: The label of the selected menu option.
        """
        options = ["List all events"]
        if role == "support":
            options.append("List my events")
        if role == "gestion":
            options.append("List unassigned events")
        if role == "commercial":
            options.append("Add event")
        if role == "gestion":
            options.append("Assign support")
        if role in ("support", "gestion"):
            options.append("Edit event")
        options.append("Back")

        choice = display_menu("Events Menu", options)
        return options[choice - 1]

    def display_event_table(self, events: List, title: str = "Events") -> None:
        """Display a table of events.

        Args:
            events: List of Event objects to display.
            title: Optional title for the table. Defaults to "Events".
        """
        if not events:
            msg = "No events found."
            display_info(msg, clear=False)
            return

        cols = [
            "ID",
            "Contract",
            "Client",
            "Name",
            "Start",
            "End",
            "Location",
            "Attendees",
            "Support",
            "Notes",
        ]
        table = create_table(title, cols)
        for event in events:
            client_name = (
                getattr(event.contract, "client", None).fullname
                if hasattr(event, "contract") and getattr(event, "contract", None)
                else "-"
            )
            support_user = getattr(event, "support_contact", None)
            support_name = (
                support_user.fullname
                if support_user and hasattr(support_user, "fullname")
                else str(getattr(event, "support_contact_id", "-"))
            )

            notes_preview = (event.notes or "")[:40]
            if event.notes and len(event.notes) > 40:
                notes_preview += "…"

            table.add_row(
                str(event.id),
                str(getattr(event, "contract_id", "-")),
                client_name,
                event.name,
                str(event.start_date),
                str(event.end_date),
                event.location,
                str(event.attendees),
                support_name,
                notes_preview,
            )
        self.console.print(table)

    def prompt_new_event(self) -> Dict[str, Any]:
        """
        Prompt for new event data.

        Returns:
            Dict containing the new event's information:
                - contract_id: ID of the associated contract (int)
                - name: Name of the event (str)
                - start_date: Start date and time (str, format: YYYY-MM-DD HH:MM)
                - end_date: End date and time (str, format: YYYY-MM-DD HH:MM)
                - location: Event location (str)
                - attendees: Number of attendees (int)
                - notes: Optional notes (str or None)

        Raises:
            CrmInvalidValue: If contract_id or attendees are not valid numbers.
        """
        contract_id = self.console.input("Contract ID: ")
        name = self.console.input("Event name: ")
        start = self.console.input("Start (YYYY-MM-DD HH:MM): ")
        end = self.console.input("End   (YYYY-MM-DD HH:MM): ")
        location = self.console.input("Location: ")
        attendees = self.console.input("Attendees: ")
        notes = self.console.input("Notes (optional): ")

        if not contract_id.isdigit():
            raise CrmInvalidValue("Contract ID must be a number.")
        if not attendees.isdigit():
            raise CrmInvalidValue("Attendees must be a number.")

        return {
            "contract_id": int(contract_id),
            "name": name,
            "start_date": start,
            "end_date": end,
            "location": location,
            "attendees": int(attendees),
            "notes": notes or None,
        }

    def prompt_event_id(self) -> int:
        """Prompt for an event ID.

        Returns:
            int: The event ID entered by the user.

        Raises:
            CrmInvalidValue: If the input is not a valid integer.
        """
        val = self.console.input("Event ID to edit: ")
        if not val.isdigit():
            raise CrmInvalidValue("Invalid ID")
        return int(val)

    def prompt_edit_event(self, event) -> Dict[str, Any]:
        """Prompt for updated event information.

        Args:
            event: The Event object being edited.

        Returns:
            Dict containing the updated event information with optional keys:
                - name: New name (str, optional)
                - start_date: New start date (str, optional)
                - end_date: New end date (str, optional)
                - location: New location (str, optional)
                - attendees: New number of attendees (int, optional)
                - notes: New notes (str, optional)

        Raises:
            CrmInvalidValue: If attendees is not a valid number.
        """
        self.console.print(
            "[italic]Press Enter to keep current value.[/italic]")

        name = self.console.input(
            f"New name ([cyan]{event.name}[/cyan]): ").strip() or None

        start = self.console.input(
            f"New start ([cyan]{event.start_date}[/cyan]): ").strip() or None

        end = self.console.input(
            f"New end   ([cyan]{event.end_date}[/cyan]): ").strip() or None

        location = self.console.input(
            f"New location ([cyan]{event.location}[/cyan]): ").strip() or None

        attendees = self.console.input(
            f"New attendees ([cyan]{event.attendees}[/cyan]): ").strip()

        notes = self.console.input(
            f"New notes ([cyan]{event.notes}[/cyan]): ").strip() or None

        if attendees and not attendees.isdigit():
            raise CrmInvalidValue("Attendees must be a number.")

        return {
            "name": name,
            "start_date": start,
            "end_date": end,
            "location": location,
            "attendees": int(attendees) if attendees else None,
            "notes": notes,
        }

    def prompt_assign_support(self) -> Tuple[int, int]:
        """
        Prompt for event ID and support user ID to assign.

        Returns:
            Tuple[int, int]: A tuple containing (event_id, support_user_id).

        Raises:
            CrmInvalidValue: If either ID is not a valid integer.
        """
        eid = self.console.input("Event ID: ")
        sid = self.console.input("Support user ID: ")
        if not eid.isdigit() or not sid.isdigit():
            raise CrmInvalidValue("Invalid ID")
        return int(eid), int(sid)

    def show_success(self, message: str) -> None:
        """Display a success message.

        Args:
            message: The success message to display.
        """
        display_success(message)

    def show_error(self, message: str) -> None:
        """Display an error message.

        Args:
            message: The error message to display.
        """
        display_error(message)

    def show_info(self, message: str) -> None:
        """Display an informational message.

        Args:
            message: The info message to display.
        """
        display_info(message)
