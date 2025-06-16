import datetime
from unittest.mock import MagicMock, patch
from exceptions import CrmNotFoundError
from tests.conftest import _make_console


def test_events_view_list_all_empty(session):
    from views.event_view import EventsView

    console = _make_console()
    view = EventsView(user=MagicMock(role=MagicMock(value="support")), console=console, session=session)

    with patch("views.event_view.EventController.list_all_events", return_value=[]), \
         patch("views.event_view.display_info") as mock_info:
        view.list_all()
        mock_info.assert_called_once_with("No events found.")


def test_events_view_list_all_with_data(session):
    from views.event_view import EventsView

    console = _make_console()
    
    event = MagicMock()
    event.id = 1
    event.name = "Kickoff"
    event.start_date = datetime.datetime(2025, 1, 1, 10, 0)
    event.end_date = datetime.datetime(2025, 1, 1, 12, 0)
    event.location = "Paris"
    event.attendees = 50
    event.notes = ""
    view = EventsView(user=MagicMock(role=MagicMock(value="support")), console=console, session=session)

    with patch("views.event_view.EventController.list_all_events", return_value=[event]) as mock_list, \
         patch("views.event_view.create_table") as mock_table:
        table = MagicMock()
        mock_table.return_value = table
        view.list_all()
        mock_list.assert_called_once()
        table.add_row.assert_called_once_with(str(event.id), event.name, str(event.start_date), str(event.end_date), event.location, str(event.attendees))


def test_events_view_add_event_invalid_attendees(session):
    from views.event_view import EventsView

    console = _make_console()
    console.input.side_effect = ["1", "Conf", "2025-01-01 10:00", "2025-01-01 12:00", "Paris", "not-number"]
    view = EventsView(user=MagicMock(role=MagicMock(value="commercial")), console=console, session=session)

    with patch("views.event_view.display_error") as mock_error, \
         patch("views.event_view.EventController.create_event") as mock_create:
        view.add_event()
        mock_error.assert_called_once_with("Attendees must be a positive integer.")
        mock_create.assert_not_called()


def test_events_view_add_event_success(session):
    from views.event_view import EventsView

    console = _make_console()
    console.input.side_effect = [
        "2", "Conf", "2025-01-01 10:00", "2025-01-01 12:00", "Paris", "30", "Notes"
    ]
    view = EventsView(user=MagicMock(role=MagicMock(value="commercial")), console=console, session=session)
    mock_event = MagicMock(id=77)
    with patch("views.event_view.EventController.create_event", return_value=mock_event) as mock_create, \
         patch("views.event_view.display_success") as mock_success:
        view.add_event()
        mock_create.assert_called_once_with(2, "Conf", "2025-01-01 10:00", "2025-01-01 12:00", "Paris", 30, "Notes")
        mock_success.assert_called_once_with("Created event ID 77")


def test_events_view_assign_support_invalid_ids(session):
    from views.event_view import EventsView

    console = _make_console()
    console.input.side_effect = ["x", "3"]
    view = EventsView(user=MagicMock(role=MagicMock(value="gestion")), console=console, session=session)

    with patch("views.event_view.display_error") as mock_error, \
         patch("views.event_view.EventController.assign_support_to_event") as mock_assign:
        view.assign_support()
        mock_error.assert_called_once_with("Invalid ID")
        mock_assign.assert_not_called()


def test_events_view_edit_event_not_found(session):
    from views.event_view import EventsView

    console = _make_console()
    console.input.return_value = "99"
    view = EventsView(user=MagicMock(role=MagicMock(value="support")), console=console, session=session)

    with patch("views.event_view.EventController.get_event_by_id", side_effect=CrmNotFoundError("Event")) as mock_get, \
         patch("views.event_view.display_error") as mock_error:
        view.edit_event()
        mock_get.assert_called_once_with(99)
        mock_error.assert_called_once()
