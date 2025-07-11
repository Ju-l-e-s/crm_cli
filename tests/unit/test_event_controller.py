from datetime import datetime
from decimal import Decimal

import pytest
from unittest.mock import patch, MagicMock

from controllers.event_controller import EventController
from controllers.repositories.event_repository import EventRepository
from controllers.repositories.contract_repository import ContractRepository
from controllers.repositories.user_repository import UserRepository
from exceptions import CrmInvalidValue, CrmNotFoundError, CrmIntegrityError
from models.event import Event
from models.contract import Contract
from tests.conftest import make_console


# --- Tests for _create_event --------------------------------------------------

def test_create_event_success(monkeypatch, seeded_user_commercial):
    ctrl = EventController(None, seeded_user_commercial, make_console())
    fake_contract = Contract(
        client_id=10,
        commercial_id=seeded_user_commercial.id,
        total_amount=Decimal('100'),
        remaining_amount=Decimal('100'),
        creation_date=datetime.now(),
        end_date=datetime.now().date(),
        is_signed=True
    )
    fake_evt = Event(
        contract_id=10,
        name="Simpsons Gala",
        start_date=datetime.now(),
        end_date=datetime.now(),
        location="Springfield",
        attendees=128,
        notes="D'oh!"
    )

    monkeypatch.setattr(ContractRepository, 'get_by_id',
                        lambda self, cid: fake_contract)
    monkeypatch.setattr(EventRepository, 'save', lambda self, e: fake_evt)

    with patch('controllers.services.authorization.get_token_payload_or_raise',
               return_value={'role': 'commercial', 'id': seeded_user_commercial.id}), \
        patch('controllers.event_controller.get_current_user',
              return_value=seeded_user_commercial):
        evt = ctrl._create_event(
            contract_id=10,
            name="Simpsons Gala",
            start_date="2025-01-01 10:00",
            end_date="2025-01-01 12:00",
            location="Springfield",
            attendees=128,
            notes="D'oh!"
        )

    assert isinstance(evt, Event)
    assert evt.name == "Simpsons Gala"


def test_create_event_contract_not_found(monkeypatch, seeded_user_commercial):
    ctrl = EventController(None, seeded_user_commercial, make_console())
    monkeypatch.setattr(ContractRepository, 'get_by_id',
                        lambda self, cid: None)

    with patch('controllers.services.authorization.get_token_payload_or_raise',
               return_value={'role': 'commercial', 'id': seeded_user_commercial.id}), \
            patch('controllers.event_controller.get_current_user',
                  return_value=seeded_user_commercial), \
            pytest.raises(CrmNotFoundError, match="Contract"):
        ctrl._create_event(
            contract_id=999,
            name="Springfield Fling",
            start_date="2025-02-02 14:00",
            end_date="2025-02-02 16:00",
            location="Evergreen Terrace",
            attendees=42,
            notes=None
        )


def test_create_event_unsigned_contract(monkeypatch, seeded_user_commercial):
    c = Contract(
        client_id=1,
        commercial_id=seeded_user_commercial.id,
        total_amount=Decimal('1'),
        remaining_amount=Decimal('1'),
        creation_date=datetime.now(),
        end_date=datetime.now().date(),
        is_signed=False
    )
    ctrl = EventController(None, seeded_user_commercial, make_console())
    monkeypatch.setattr(ContractRepository, 'get_by_id', lambda self, cid: c)

    with patch('controllers.services.authorization.get_token_payload_or_raise',
               return_value={'role': 'commercial', 'id': seeded_user_commercial.id}), \
            patch('controllers.event_controller.get_current_user',
                  return_value=seeded_user_commercial), \
            pytest.raises(CrmInvalidValue, match="Cannot create event for unsigned contract"):
        ctrl._create_event(
            contract_id=1,
            name="Burns Roast",
            start_date="2025-03-03 10:00",
            end_date="2025-03-03 12:00",
            location="Mr. Burns Manor",
            attendees=7,
            notes="Excellent"
        )


def test_create_event_wrong_owner(monkeypatch, seeded_user_commercial):
    other_contract = Contract(
        client_id=1,
        commercial_id=999,
        total_amount=Decimal('1'),
        remaining_amount=Decimal('1'),
        creation_date=datetime.now(),
        end_date=datetime.now().date(),
        is_signed=True
    )
    ctrl = EventController(None, seeded_user_commercial, make_console())
    monkeypatch.setattr(ContractRepository, 'get_by_id',
                        lambda self, cid: other_contract)

    with patch('controllers.services.authorization.get_token_payload_or_raise',
               return_value={'role': 'commercial', 'id': seeded_user_commercial.id}), \
            patch('controllers.event_controller.get_current_user',
                  return_value=seeded_user_commercial), \
            pytest.raises(CrmInvalidValue, match="only create events for your own contracts"):
        ctrl._create_event(
            contract_id=1,
            name="Moleman's Meetup",
            start_date="2025-04-04 18:00",
            end_date="2025-04-04 20:00",
            location="Moleman's basement",
            attendees=3,
            notes=None
        )


def test_create_event_validation_error(monkeypatch, seeded_user_commercial):
    ctrl = EventController(None, seeded_user_commercial, make_console())
    monkeypatch.setattr(ContractRepository, 'get_by_id',
                        lambda self, cid: Contract(
                            client_id=1,
                            commercial_id=seeded_user_commercial.id,
                            total_amount=Decimal('1'),
                            remaining_amount=Decimal('1'),
                            creation_date=datetime.now(),
                            end_date=datetime.now().date(),
                            is_signed=True
                        ))
    monkeypatch.setattr('controllers.event_controller.validate_event_name',
                        lambda n: (_ for _ in ()).throw(CrmInvalidValue("bad name")))

    with patch('controllers.services.authorization.get_token_payload_or_raise',
               return_value={'role': 'commercial', 'id': seeded_user_commercial.id}), \
            patch('controllers.event_controller.get_current_user',
                  return_value=seeded_user_commercial), \
            pytest.raises(CrmInvalidValue, match="bad name"):
        ctrl._create_event(
            contract_id=1,
            name="bad name",
            start_date="2025-05-05 10:00",
            end_date="2025-05-05 12:00",
            location="Shelbyville",
            attendees=1,
            notes=None
        )


# --- Tests for get_event_by_id --------------------------------------------------

def test_get_event_by_id_success(monkeypatch, seeded_user):
    ctrl = EventController(None, seeded_user, make_console())
    fake = MagicMock()
    monkeypatch.setattr(EventRepository, 'get_by_id', lambda self, eid: fake)
    assert ctrl.get_event_by_id(5) is fake


def test_get_event_by_id_not_found(monkeypatch, seeded_user):
    ctrl = EventController(None, seeded_user, make_console())
    monkeypatch.setattr(EventRepository, 'get_by_id', lambda self, eid: None)
    with pytest.raises(CrmNotFoundError, match="Event"):
        ctrl.get_event_by_id(5)


# --- Tests for _update_event --------------------------------------------------

def test_update_event_success(monkeypatch, seeded_user):
    existing = Event(
        name="Marge's Brunch",
        start_date=datetime.now(),
        end_date=datetime.now(),
        location="Springfield Church",
        attendees=8,
        notes="Delicious",
        contract_id=1
    )
    existing.id = 7
    updated = Event(
        name="Marge's Gala",
        start_date=datetime.now(),
        end_date=datetime.now(),
        location="Springfield Church",
        attendees=12,
        notes="Finer",
        contract_id=1
    )
    updated.id = 7

    monkeypatch.setattr(EventRepository, 'get_by_id',
                        lambda self, eid: existing)
    monkeypatch.setattr(EventRepository, 'save', lambda self, e: updated)

    ctrl = EventController(None, seeded_user, make_console())
    with patch('controllers.services.authorization.get_token_payload_or_raise',
               return_value={'role': 'gestion', 'id': seeded_user.id}), \
        patch('controllers.event_controller.get_current_user',
              return_value=seeded_user):
        result = ctrl._update_event(
            event_id=7,
            name="Marge's Gala",
            start_date=None,
            end_date=None,
            location=None,
            attendees=12,
            notes=None
        )

    assert isinstance(result, Event)
    assert result.attendees == 12


def test_update_event_not_found(monkeypatch, seeded_user):
    ctrl = EventController(None, seeded_user, make_console())
    monkeypatch.setattr(EventRepository, 'get_by_id', lambda self, eid: None)
    with pytest.raises(CrmNotFoundError, match="Event"):
        ctrl._update_event(
            event_id=1,
            name=None,
            start_date=None,
            end_date=None,
            location=None,
            attendees=None,
            notes=None
        )


def test_update_event_validation_error(monkeypatch, seeded_user):
    e = Event(
        name="Burns' Banquet",
        start_date=datetime.now(),
        end_date=datetime.now(),
        location="Burns' Mansion",
        attendees=20,
        notes="Fanciest",
        contract_id=1
    )
    e.id = 3
    monkeypatch.setattr(EventRepository, 'get_by_id', lambda self, eid: e)
    monkeypatch.setattr('controllers.event_controller.validate_location',
                        lambda loc: (_ for _ in ()).throw(CrmInvalidValue("bad loc")))

    ctrl = EventController(None, seeded_user, make_console())
    with patch('controllers.services.authorization.get_token_payload_or_raise',
               return_value={'role': 'gestion', 'id': seeded_user.id}), \
            patch('controllers.event_controller.get_current_user',
                  return_value=seeded_user), \
            pytest.raises(CrmInvalidValue, match="bad loc"):
        ctrl._update_event(
            event_id=3,
            name=None,
            start_date=None,
            end_date=None,
            location="bad loc",
            attendees=None,
            notes=None
        )


def test_update_event_repository_error(monkeypatch, seeded_user):
    e = Event(
        name="Krusty Show",
        start_date=datetime.now(),
        end_date=datetime.now(),
        location="Krusty Studios",
        attendees=100,
        notes="LOL",
        contract_id=1
    )
    e.id = 4
    monkeypatch.setattr(EventRepository, 'get_by_id', lambda self, eid: e)
    monkeypatch.setattr(EventRepository, 'save',
                        lambda self, evt: (_ for _ in ()).throw(Exception("Fail")))

    ctrl = EventController(None, seeded_user, make_console())
    with patch('controllers.services.authorization.get_token_payload_or_raise',
               return_value={'role': 'gestion', 'id': seeded_user.id}), \
            patch('controllers.event_controller.get_current_user',
                  return_value=seeded_user), \
            pytest.raises(CrmIntegrityError, match="Could not update event: Fail"):
        ctrl._update_event(
            event_id=4,
            name=None,
            start_date=None,
            end_date=None,
            location=None,
            attendees=None,
            notes=None
        )


# --- Tests for list_*_events --------------------------------------------------

def test_list_all_events(monkeypatch, seeded_user):
    ctrl = EventController(None, seeded_user, make_console())
    fake = [MagicMock(), MagicMock()]
    monkeypatch.setattr(EventRepository, 'list_all', lambda self: fake)
    ctrl.view.display_event_table = MagicMock()

    ctrl.list_all_events()
    ctrl.view.display_event_table.assert_called_once_with(
        fake, title="All Events")


def test_list_my_events(monkeypatch, seeded_user_commercial):
    ctrl = EventController(None, seeded_user_commercial, make_console())
    monkeypatch.setattr(EventRepository, 'list_by_support_contact',
                        lambda self, uid: ["Duff"])
    ctrl.view.display_event_table = MagicMock()

    with patch('controllers.services.authorization.get_token_payload_or_raise',
               return_value={'role': 'support', 'id': seeded_user_commercial.id}):
        ctrl.list_my_events()

    ctrl.view.display_event_table.assert_called_once_with(
        ["Duff"], title="My Events")


def test_list_unassigned_events(monkeypatch, seeded_user):
    ctrl = EventController(None, seeded_user, make_console())
    monkeypatch.setattr(EventRepository, 'list_without_support',
                        lambda self: ["Sideshow Bob"])
    ctrl.view.display_event_table = MagicMock()

    with patch('controllers.services.authorization.get_token_payload_or_raise',
               return_value={'role': 'gestion', 'id': seeded_user.id}):
        ctrl.list_unassigned_events()

    ctrl.view.display_event_table.assert_called_once_with(
        ["Sideshow Bob"], title="Unassigned Events")


# --- Tests for _assign_support --------------------------------------------------

def test_assign_support_success(monkeypatch, seeded_user):
    evt = Event(
        name="Lisa Recital",
        start_date=datetime.now(),
        end_date=datetime.now(),
        location="School",
        attendees=1,
        notes="Pride",
        contract_id=1
    )
    evt.id = 8
    monkeypatch.setattr(EventRepository, 'get_by_id', lambda self, eid: evt)
    monkeypatch.setattr(UserRepository,  'get_by_id',
                        lambda self, uid: type("U", (), {
                            "role": type("R", (), {"value": "support"}),
                            "fullname": "Milhouse"
                        })())
    monkeypatch.setattr(EventRepository, 'save', lambda self, e: evt)

    ctrl = EventController(None, seeded_user, make_console())
    with patch('controllers.services.authorization.get_token_payload_or_raise',
               return_value={'role': 'gestion', 'id': seeded_user.id}):
        updated = ctrl._assign_support(event_id=8, support_contact_id=9)

    assert updated is evt
    assert updated.support_contact_id == 9


def test_assign_support_event_not_found(monkeypatch, seeded_user):
    ctrl = EventController(None, seeded_user, make_console())
    monkeypatch.setattr(EventRepository, 'get_by_id', lambda self, eid: None)

    with patch('controllers.services.authorization.get_token_payload_or_raise',
               return_value={'role': 'gestion', 'id': seeded_user.id}), \
            pytest.raises(CrmNotFoundError, match="Event"):
        ctrl._assign_support(1, 2)


def test_assign_support_user_not_found(monkeypatch, seeded_user):
    evt = Event(
        name="Moe’s Night",
        start_date=datetime.now(),
        end_date=datetime.now(),
        location="Moe’s Tavern",
        attendees=20,
        notes=None,
        contract_id=1
    )
    evt.id = 9
    ctrl = EventController(None, seeded_user, make_console())
    monkeypatch.setattr(EventRepository, 'get_by_id', lambda self, eid: evt)
    monkeypatch.setattr(UserRepository,  'get_by_id', lambda self, uid: None)

    with patch('controllers.services.authorization.get_token_payload_or_raise',
               return_value={'role': 'gestion', 'id': seeded_user.id}), \
            pytest.raises(CrmNotFoundError, match="Support user"):
        ctrl._assign_support(9, 2)


def test_assign_support_wrong_role(monkeypatch, seeded_user):
    evt = Event(
        name="Springfield BBQ",
        start_date=datetime.now(),
        end_date=datetime.now(),
        location="Simpson’s Yard",
        attendees=30,
        notes=None,
        contract_id=1
    )
    evt.id = 10
    ctrl = EventController(None, seeded_user, make_console())
    monkeypatch.setattr(EventRepository, 'get_by_id', lambda self, eid: evt)
    monkeypatch.setattr(UserRepository,  'get_by_id',
                        lambda self, uid: type("U", (), {
                            "role": type("R", (), {"value": "commercial"})
                        })())

    with patch('controllers.services.authorization.get_token_payload_or_raise',
               return_value={'role': 'gestion', 'id': seeded_user.id}), \
            pytest.raises(CrmInvalidValue, match="User must have support role"):
        ctrl._assign_support(10, 5)


def test_assign_support_repository_error(monkeypatch, seeded_user):
    evt = Event(
        name="Itchy & Scratchy",
        start_date=datetime.now(),
        end_date=datetime.now(),
        location="TV Studio",
        attendees=2,
        notes=None,
        contract_id=1
    )
    evt.id = 11
    ctrl = EventController(None, seeded_user, make_console())
    monkeypatch.setattr(EventRepository, 'get_by_id', lambda self, eid: evt)
    monkeypatch.setattr(UserRepository,  'get_by_id',
                        lambda self, uid: type("U", (), {
                            "role": type("R", (), {"value": "support"})
                        })())
    monkeypatch.setattr(EventRepository, 'save',
                        lambda self, e: (_ for _ in ()).throw(Exception("Fault")))

    with patch('controllers.services.authorization.get_token_payload_or_raise',
               return_value={'role': 'gestion', 'id': seeded_user.id}), \
            pytest.raises(CrmIntegrityError, match="Could not assign support to event: Fault"):
        ctrl._assign_support(11, 9)
