from exceptions import CrmInvalidValue, CrmNotFoundError
from views.base import display_menu, display_error, display_success, create_table, display_info

from controllers.event_controller import EventController


class EventsView:
    def __init__(self, user, console, session):
        self.user = user
        self.console = console
        self.controller = EventController(session)

    def show_menu(self):
        """
        Display the events menu and handle user input.
        """
        while True:
            options = [
                ("List all events", self.list_all),
                ("List my events",
                 self.list_mine) if self.user.role.value == "support" else None,
                ("List without support",
                 self.list_unassigned) if self.user.role.value == "gestion" else None,
                ("Add event", self.add_event) if self.user.role.value == "commercial" else None,
                ("Assign support",
                 self.assign_support) if self.user.role.value == "gestion" else None,
                ("Edit event", self.edit_event) if self.user.role.value in (
                    "commercial", "support", "gestion") else None,
                ("Back", lambda: "back"),
            ]
            valid_options = [opt for opt in options if opt]
            choice_idx = display_menu(
                "Events Menu", [label for label, _ in valid_options]) - 1
            _, action = valid_options[choice_idx]
            if action() == "back":
                break

    def list_all(self):
        try:
            events = self.controller.list_all_events()
            if not events:
                display_info("No events found.")
                return

            table = create_table(
                "All Events", ["ID", "Name", "Start", "End", "Location", "Attendees"])
            for e in events:
                table.add_row(str(e.id), e.name, str(e.start_date), str(
                    e.end_date), e.location, str(e.attendees))
            self.console.print(table)
        except (CrmInvalidValue, CrmNotFoundError) as e:
            display_error(str(e))

    def list_mine(self):
        try:
            events = self.controller.list_my_events()
            if not events:
                display_info(
                    "You don't have any events assigned to you.", clear=False)
                return

            table = create_table("My Events", ["ID", "Name"])
            for e in events:
                table.add_row(str(e.id), e.name)
            self.console.print(table)
        except (CrmInvalidValue, CrmNotFoundError) as e:
            display_error(str(e))

    def list_unassigned(self):
        try:
            events = self.controller.list_events_without_support()
            if not events:
                display_info("No unassigned events found.")
                return

            table = create_table("Unassigned Events", ["ID", "Name"])
            for e in events:
                table.add_row(str(e.id), e.name)
            self.console.print(table)
        except (CrmInvalidValue, CrmNotFoundError) as e:
            display_error(str(e))

    def add_event(self):
        contract_id = self.console.input("Contract ID: ")
        name = self.console.input("Event name: ")
        start_date = self.console.input("Start (YYYY-MM-DD HH:MM): ")
        end_date = self.console.input("End   (YYYY-MM-DD HH:MM): ")
        location = self.console.input("Location: ")
        attendees = self.console.input("Attendees: ")
        if not attendees.isdigit():
            display_error("Attendees must be a positive integer.")
            return
        notes = self.console.input("Notes (optional): ")
        try:
            e = self.controller.create_event(
                int(contract_id), name, start_date, end_date, location, int(attendees), notes)
            display_success(f"Created event ID {e.id}")
        except (CrmInvalidValue, CrmNotFoundError) as e:
            display_error(str(e))

    def assign_support(self):
        event_id = self.console.input("Event ID: ")
        support_id = self.console.input("Support user ID: ")
        if not event_id.isdigit() or not support_id.isdigit():
            display_error("Invalid ID")
            return
        try:
            e = self.controller.assign_support_to_event(
                int(event_id), int(support_id))
            display_success(
                f"Assigned support ID {support_id} to event ID {e.id}")
        except (CrmInvalidValue, CrmNotFoundError) as e:
            display_error(str(e))

    def edit_event(self):
        event_id = self.console.input("Event ID to edit: ")
        if not event_id.isdigit():
            display_error("Invalid ID")
            return
        try:
            event = self.controller.get_event_by_id(int(event_id))
        except CrmNotFoundError as e:
            display_error(str(e))
            return
        self.console.print("[italic]Press Enter to keep the current value.[/italic]")
        name = self.console.input("New name ([cyan]{event.name}[/cyan]): ").strip()
        start = self.console.input("New start ([cyan]{event.start_date}[/cyan]): ").strip()
        end = self.console.input("New end ([cyan]{event.end_date}[/cyan]): ").strip()
        location = self.console.input("New location ([cyan]{event.location}[/cyan]): ").strip()
        attendees = self.console.input("New attendees ([cyan]{event.attendees}[/cyan]): ").strip()
        if attendees and not attendees.isdigit():
            display_error("Attendees must be a positive integer.")
            return
        notes = self.console.input(f"New notes ([cyan]{event.notes}[/cyan]): ").strip()
        update_data = {
            'name':     name or event.name,
            'start_date': start or str(event.start_date),
            'end_date':   end or str(event.end_date),
            'location': location or event.location,
            'attendees': int(attendees) if attendees else event.attendees,
            'notes':    notes or event.notes,
        }
        try:
            event = self.controller.update_event(int(event_id), **update_data)
            display_success(f"Updated event ID {event.id}")
        except (CrmInvalidValue, CrmNotFoundError) as e:
            display_error(str(e))
