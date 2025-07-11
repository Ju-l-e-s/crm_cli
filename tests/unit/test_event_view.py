import pytest
from exceptions import CrmInvalidValue
from tests.conftest import make_console
from views.event_view import EventsView
from unittest.mock import MagicMock, patch


class DummyClient:
    def __init__(self, fullname):
        self.fullname = fullname


class DummyContract:
    def __init__(self, client):
        self.client = client


class DummySupport:
    def __init__(self, fullname):
        self.fullname = fullname


class DummyEvent:
    def __init__(
        self,
        id=1,
        contract_id=2,
        contract=None,
        name="E",
        start_date="2025-01-01 10:00",
        end_date="2025-01-01 12:00",
        location="Loc",
        attendees=10,
        support_contact=None,
        support_contact_id=99,
        notes=None,
    ):
        self.id = id
        self.contract_id = contract_id
        self.contract = contract
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.location = location
        self.attendees = attendees
        self.support_contact = support_contact
        self.support_contact_id = support_contact_id
        self.notes = notes


def test_show_menu_support(monkeypatch):
    console = make_console()
    monkeypatch.setattr("views.event_view.display_menu",
                        lambda title, opts: opts.index("List my events") + 1)
    view = EventsView(console)
    assert view.show_menu("support") == "List my events"


def test_show_menu_gestion(monkeypatch):
    console = make_console()
    monkeypatch.setattr("views.event_view.display_menu",
                        lambda title, opts: opts.index("Assign support") + 1)
    view = EventsView(console)
    assert view.show_menu("gestion") == "Assign support"


def test_show_menu_commercial(monkeypatch):
    console = make_console()
    monkeypatch.setattr("views.event_view.display_menu",
                        lambda title, opts: opts.index("Add event") + 1)
    view = EventsView(console)
    assert view.show_menu("commercial") == "Add event"


def test_show_menu_back_always_available(monkeypatch):
    console = make_console()
    monkeypatch.setattr("views.event_view.display_menu",
                        lambda title, opts: len(opts))
    view = EventsView(console)
    for role in ("support", "gestion", "commercial", "other"):
        assert view.show_menu(role) == "Back"


def test_display_event_table_empty(monkeypatch):
    console = make_console()
    mock_display_info = MagicMock()
    monkeypatch.setattr('views.event_view.display_info', mock_display_info)

    view = EventsView(console)
    view.display_event_table([], title="Some Title")

    mock_display_info.assert_called_once_with("No events found.", clear=False)


def test_display_event_table_with_data(monkeypatch):
    console = make_console()
    client = DummyClient("Alice")
    contract = DummyContract(client)
    support = DummySupport("Bob")
    evts = [
        DummyEvent(
            id=5,
            contract_id=7,
            contract=contract,
            name="X",
            start_date="S",
            end_date="E",
            location="L",
            attendees=3,
            support_contact=support,
            notes="notes here"
        ),
    ]
    view = EventsView(console)
    with patch("views.event_view.create_table") as mock_create_table:
        table_mock = MagicMock()
        mock_create_table.return_value = table_mock
        view.display_event_table(evts, title="T")
        mock_create_table.assert_called_once()
        table_mock.add_row.assert_called_once_with(
            "5", "7", "Alice", "X", "S", "E", "L", "3", "Bob", "notes here"
        )
        console.print.assert_called_once_with(table_mock)


def test_prompt_new_event_success():
    console = make_console()
    console.input.side_effect = ["10", "MyEvent",
                                 "A", "B", "Paris", "42", "Some notes"]
    view = EventsView(console)
    data = view.prompt_new_event()
    assert data == {
        "contract_id": 10,
        "name": "MyEvent",
        "start_date": "A",
        "end_date": "B",
        "location": "Paris",
        "attendees": 42,
        "notes": "Some notes",
    }


def test_prompt_new_event_invalid_contract():
    console = make_console()
    console.input.side_effect = ["x", "n", "n", "n", "n", "n", ""]
    view = EventsView(console)
    with pytest.raises(CrmInvalidValue):
        view.prompt_new_event()


def test_prompt_new_event_invalid_attendees():
    console = make_console()
    console.input.side_effect = ["1", "n", "n", "n", "n", "bad", ""]
    view = EventsView(console)
    with pytest.raises(CrmInvalidValue):
        view.prompt_new_event()


def test_prompt_event_id_valid_and_invalid():
    console = make_console()
    console.input.return_value = "99"
    view = EventsView(console)
    assert view.prompt_event_id() == 99

    console.input.return_value = "bad"
    with pytest.raises(CrmInvalidValue):
        view.prompt_event_id()


def test_prompt_edit_event_keep_and_invalid():
    console = make_console()
    console.input.side_effect = ["", "", "", "", "bad", ""]
    evt = DummyEvent(name="N", start_date="S", end_date="E",
                     location="L", attendees=7, notes="Z")
    view = EventsView(console)
    with pytest.raises(CrmInvalidValue):
        view.prompt_edit_event(evt)

    console = make_console()
    console.input.side_effect = ["", "", "", "", "8", ""]
    view = EventsView(console)
    data = view.prompt_edit_event(evt)
    assert data == {
        "name": None,
        "start_date": None,
        "end_date": None,
        "location": None,
        "attendees": 8,
        "notes": None,
    }


def test_prompt_assign_support_valid_and_invalid():
    console = make_console()
    console.input.side_effect = ["7", "8"]
    view = EventsView(console)
    assert view.prompt_assign_support() == (7, 8)

    console.input.side_effect = ["x", "8"]
    with pytest.raises(CrmInvalidValue):
        view.prompt_assign_support()

    console.input.side_effect = ["7", "y"]
    with pytest.raises(CrmInvalidValue):
        view.prompt_assign_support()


def test_show_messages(monkeypatch):
    console = make_console()
    view = EventsView(console)
    called = {}
    monkeypatch.setattr("views.event_view.display_success",
                        lambda msg: called.setdefault("ok", msg))
    monkeypatch.setattr("views.event_view.display_error",
                        lambda msg: called.setdefault("err", msg))
    monkeypatch.setattr("views.event_view.display_info",
                        lambda msg: called.setdefault("info", msg))

    view.show_success("Done")
    view.show_error("Oops")
    view.show_info("Hello")
    assert called == {"ok": "Done", "err": "Oops", "info": "Hello"}
