import pytest
from exceptions import CrmInvalidValue
from controllers.services.authorization import requires_role, requires_self_or_role


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

    with pytest.raises(CrmInvalidValue, match="Forbidden"):
        wrapped_func()


def test_requires_role_missing_token(monkeypatch):
    monkeypatch.setattr("controllers.services.authorization.load_token", lambda: None)

    with pytest.raises(CrmInvalidValue, match="Authentication required"):
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

    with pytest.raises(CrmInvalidValue, match="Forbidden"):
        wrapped_func2(user_id=123)


def test_requires_self_or_role_no_token(monkeypatch):
    monkeypatch.setattr("controllers.services.authorization.load_token", lambda: None)

    with pytest.raises(CrmInvalidValue, match="Authentication required"):
        wrapped_func2(user_id=123)