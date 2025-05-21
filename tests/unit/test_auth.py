import pytest

from exceptions import CrmInvalidValue
from services.auth import generate_token, decode_token, get_user_from_token
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
    with pytest.raises(CrmInvalidValue) as excinfo:
        get_user_from_token("invalid.token", session)
    assert "Invalid token." in str(excinfo.value)

def test_expired_token(session, seeded_user):
    from services.auth import JWT_SECRET
    expired_payload = {
        "id": seeded_user.id,
        "role": seeded_user.role.value,
        "exp": datetime.now(timezone.utc) - timedelta(seconds=1)
    }
    expired_token = jwt.encode(expired_payload, JWT_SECRET, algorithm="HS256")

    with pytest.raises(CrmInvalidValue) as excinfo:
        get_user_from_token(expired_token, session)
    assert "Token expired." in str(excinfo.value)
