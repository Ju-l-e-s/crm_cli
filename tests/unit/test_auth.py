import pytest
from exceptions import CrmAuthenticationError, CrmNotFoundError, CrmIntegrityError

from exceptions import CrmInvalidValue
from controllers.services.auth import generate_token, decode_token, get_user_from_token, get_current_user
import jwt
from datetime import datetime, timedelta, timezone


def test_generate_and_decode_token(session,seeded_user):
    token = generate_token(seeded_user)
    payload = decode_token(token)

    assert payload["id"] == seeded_user.id
    assert payload["role"] == seeded_user.role.value

def test_get_user_from_token_valid(session, seeded_user):
    token = generate_token(seeded_user)
    found_user = get_user_from_token(token, session)

    assert found_user is not None
    assert found_user.id == seeded_user.id

def test_get_user_from_token_invalid(session):
    with pytest.raises(CrmAuthenticationError) as excinfo:
        get_user_from_token("invalid.token", session)
    assert "Invalid token." in str(excinfo.value)

def test_expired_token(session, seeded_user,monkeypatch):
    monkeypatch.setattr("controllers.services.auth.JWT_SECRET", "test-secret")
    expired_payload = {
        "id": seeded_user.id,
        "role": seeded_user.role.value,
        "exp": datetime.now(timezone.utc) - timedelta(seconds=1)
    }
    expired_token = jwt.encode(expired_payload, "test-secret", algorithm="HS256")

    with pytest.raises(CrmAuthenticationError) as excinfo:
        get_user_from_token(expired_token, session)
    assert "Token expired." in str(excinfo.value)

def test_expired_token_deletes_cache(session, seeded_user, tmp_path, monkeypatch):
    token_file = tmp_path / "token.jwt"
    monkeypatch.setattr("controllers.services.token_cache.TOKEN_PATH", token_file)
    monkeypatch.setattr("controllers.services.auth.JWT_SECRET", "test-secret")

    expired_payload = {
        "id": seeded_user.id,
        "role": seeded_user.role.value,
        "exp": datetime.now(timezone.utc) - timedelta(days=1)
    }
    token_file.write_text(jwt.encode(expired_payload, "test-secret", algorithm="HS256"))

    with pytest.raises(CrmAuthenticationError, match="Token expired."):
        get_user_from_token(token_file.read_text(), session)

    assert not token_file.exists()

def test_get_current_user_valid(session,seeded_user,monkeypatch):
    payload = {
        "id": seeded_user.id,
        "role": seeded_user.role.value,
        "exp": datetime.now(timezone.utc) + timedelta(hours=1)
    }
    monkeypatch.setattr("controllers.services.auth.load_token", lambda: "test-token")
    monkeypatch.setattr("controllers.services.auth.decode_token", lambda token: payload)
    assert get_current_user(session) == seeded_user

def test_get_current_user_invalid(session,seeded_user,monkeypatch):
    monkeypatch.setattr("controllers.services.auth.load_token", lambda: "some.invalid.token")
    def fake_decode(token): raise CrmAuthenticationError("Invalid token.")
    monkeypatch.setattr("controllers.services.auth.decode_token", fake_decode)

    with pytest.raises(CrmAuthenticationError, match="Invalid token."):
        get_current_user(session)

def test_get_current_user_expired(session,seeded_user,monkeypatch):

    monkeypatch.setattr("controllers.services.auth.load_token", lambda: "test-token")

    def fake_decode_token(token):
        raise CrmAuthenticationError("Token expired.")

    monkeypatch.setattr("controllers.services.auth.decode_token", fake_decode_token)
    with pytest.raises(CrmAuthenticationError, match="Token expired."):
        get_current_user(session)