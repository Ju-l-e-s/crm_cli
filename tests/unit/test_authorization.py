from unittest.mock import MagicMock

import pytest
from exceptions import CrmAuthenticationError, CrmNotFoundError
from exceptions import CrmForbiddenAccessError, CrmInvalidValue
from controllers.services.authorization import requires_role, requires_self_or_role, get_event_owner_id


@requires_role("gestion")
def wrapped_func():
    return "Access granted"


def test_requires_role_ok(monkeypatch):
    monkeypatch.setattr("controllers.services.authorization.load_token", lambda: "valid_token")
    monkeypatch.setattr("controllers.services.authorization.decode_token", lambda token: {"role": "gestion"})

    assert wrapped_func() == "Access granted"


def test_requires_role_invalid(monkeypatch):
    monkeypatch.setattr("controllers.services.authorization.load_token", lambda: "valid_token")
    monkeypatch.setattr("controllers.services.authorization.decode_token", lambda token: {"role": "support"})

    with pytest.raises(CrmForbiddenAccessError, match="Forbidden"):
        wrapped_func()


def test_requires_role_missing_token(monkeypatch):
    monkeypatch.setattr("controllers.services.authorization.load_token", lambda: None)

    with pytest.raises(CrmAuthenticationError, match="Authentication required"):
        wrapped_func()

@requires_self_or_role("gestion")
def wrapped_func2(user_id: int):
    return f"Access granted to user {user_id}"


def test_requires_self_or_role_by_role(monkeypatch):
    monkeypatch.setattr("controllers.services.authorization.load_token", lambda: "valid_token")
    monkeypatch.setattr("controllers.services.authorization.decode_token", lambda token: {"role": "gestion", "id": 999})

    assert wrapped_func2(user_id=123) == "Access granted to user 123"


def test_requires_self_or_role_by_identity(monkeypatch):
    monkeypatch.setattr("controllers.services.authorization.load_token", lambda: "valid_token")
    monkeypatch.setattr("controllers.services.authorization.decode_token", lambda token: {"role": "support", "id": 123})

    assert wrapped_func2(user_id=123) == "Access granted to user 123"


def test_requires_self_or_role_forbidden(monkeypatch):
    monkeypatch.setattr("controllers.services.authorization.load_token", lambda: "valid_token")
    monkeypatch.setattr("controllers.services.authorization.decode_token", lambda token: {"role": "support", "id": 42})

    with pytest.raises(CrmForbiddenAccessError, match="Forbidden"):
        wrapped_func2(user_id=123)


def test_requires_self_or_role_no_token(monkeypatch):
    monkeypatch.setattr("controllers.services.authorization.load_token", lambda: None)

    with pytest.raises(CrmAuthenticationError, match="Authentication required"):
        wrapped_func2(user_id=123)


def test_get_event_owner_id_ok(monkeypatch):
    session = MagicMock()
    # Create fake Event and Contract objects with MagicMock
    event = MagicMock(spec=["id", "contract_id"])
    event.id = 1
    event.contract_id = 2

    contract = MagicMock(spec=["id", "commercial_id"])
    contract.id = 2
    contract.commercial_id = 42

    # Monkey-patch des repositories
    monkeypatch.setattr(
        "controllers.repositories.event_repository.EventRepository.get_by_id",
        lambda self, eid: event if eid == 1 else None
    )
    monkeypatch.setattr(
        "controllers.repositories.contract_repository.ContractRepository.get_by_id",
        lambda self, cid: contract if cid == 2 else None
    )

    # Execution
    owner_id = get_event_owner_id(session, 1)
    assert owner_id == 42


def test_get_event_owner_id_event_not_found(monkeypatch):
    session = MagicMock()

    # No event found
    monkeypatch.setattr(
        "controllers.repositories.event_repository.EventRepository.get_by_id",
        lambda self, eid: None
    )

    with pytest.raises(CrmNotFoundError, match="Event not found."):
        get_event_owner_id(session, 1)


def test_get_event_owner_id_contract_not_found(monkeypatch):
    session = MagicMock()
    # Event found
    event = MagicMock(spec=["id", "contract_id"])
    event.id = 1
    event.contract_id = 2

    monkeypatch.setattr(
        "controllers.repositories.event_repository.EventRepository.get_by_id",
        lambda self, eid: event
    )
    # Contract not found
    monkeypatch.setattr(
        "controllers.repositories.contract_repository.ContractRepository.get_by_id",
        lambda self, cid: None
    )

    with pytest.raises(CrmNotFoundError, match="Associated contract not found."):
        get_event_owner_id(session, 1)