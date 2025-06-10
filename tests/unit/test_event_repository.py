# tests/unit/test_event_repository.py

import pytest
from datetime import datetime, timedelta

from controllers.repositories.event_repository import EventRepository
from models.event import Event


def test_event_repository_crud(session):
    repo = EventRepository(session)

    now = datetime.now()
    later = now + timedelta(hours=4)

    event = Event(
        name="Wedding Reception",
        start_date=now,
        end_date=later,
        location="Grand Hotel Ballroom",
        attendees=150,
        notes="Formal dinner at 7pm, dancing until midnight",
        contract_id=1
    )

    saved = repo.save(event)
    assert saved.id is not None
    assert saved.name == "Wedding Reception"
    assert saved.attendees == 150

    all_events = repo.list_all()
    assert isinstance(all_events, list)
    assert saved in all_events

    fetched = repo.get_by_id(saved.id)
    assert fetched.id == saved.id
    assert fetched.location == "Grand Hotel Ballroom"

    assert repo.get_by_id(99999) is None


def test_event_repository_list_by_support_contact(session):
    repo = EventRepository(session)

    now = datetime.now()
    later = now + timedelta(hours=2)

    # Event with support contact
    event1 = Event(
        name="Corporate Meeting",
        start_date=now,
        end_date=later,
        location="Conference Room A",
        attendees=50,
        contract_id=1,
        support_contact_id=10
    )

    # Event without support contact
    event2 = Event(
        name="Product Launch",
        start_date=now,
        end_date=later,
        location="Convention Center",
        attendees=200,
        contract_id=2
    )

    repo.save(event1)
    repo.save(event2)

    # Test filtering by support contact
    support_events = repo.list_by_support_contact(10)
    assert len(support_events) == 1
    assert support_events[0].name == "Corporate Meeting"

    # Test filtering events without support
    no_support_events = repo.list_without_support()
    assert len(no_support_events) >= 1
    assert any(e.name == "Product Launch" for e in no_support_events)


def test_event_repository_list_by_contract(session):
    repo = EventRepository(session)

    now = datetime.now()
    later = now + timedelta(hours=3)

    # Two events for same contract
    event1 = Event(
        name="Setup Day",
        start_date=now,
        end_date=later,
        location="Venue Hall",
        attendees=10,
        contract_id=5
    )

    event2 = Event(
        name="Main Event",
        start_date=later,
        end_date=later + timedelta(hours=5),
        location="Venue Hall",
        attendees=300,
        contract_id=5
    )

    # One event for different contract
    event3 = Event(
        name="Different Event",
        start_date=now,
        end_date=later,
        location="Other Venue",
        attendees=100,
        contract_id=6
    )

    repo.save(event1)
    repo.save(event2)
    repo.save(event3)

    # Test filtering by contract
    contract_events = repo.list_by_contract(5)
    assert len(contract_events) == 2
    event_names = [e.name for e in contract_events]
    assert "Setup Day" in event_names
    assert "Main Event" in event_names

    other_contract_events = repo.list_by_contract(6)
    assert len(other_contract_events) == 1
    assert other_contract_events[0].name == "Different Event"