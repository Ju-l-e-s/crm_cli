from sqlalchemy.orm import Session
import os
from jwt import encode, decode, ExpiredSignatureError, InvalidTokenError

from exceptions import CrmInvalidValue
from models.user import User
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

from controllers.repositories.user_repository import UserRepository
from controllers.services.token_cache import delete_token

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_EXPIRES_IN = int(os.getenv("JWT_EXPIRES_IN", 3600*24))


def generate_token(user: User) -> str:
    """
    Generates a JWT token for a user.

    :param user: The user to generate a token for.
    :return: The generated token.
    """
    exp = datetime.now(timezone.utc) + timedelta(seconds=JWT_EXPIRES_IN)
    payload = {
        "id": user.id,
        "role": user.role.value,
        "exp": exp
    }
    return encode(payload, JWT_SECRET, algorithm="HS256")

def decode_token(token: str) -> dict:
    """
    Decodes a JWT token and returns the payload.

    :param token: The token to decode.
    :return: The decoded payload.
    """
    try:
        payload = decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except ExpiredSignatureError:
        delete_token()
        raise CrmInvalidValue("Token expired.")
    except InvalidTokenError:
        delete_token()
        raise CrmInvalidValue("Invalid token.")

def get_user_from_token(token: str, session: Session) -> User | None:
    """
    Gets the user associated with a JWT token.

    :param token: The token to get the user from.
    :param session: The database session to use.
    :return: The user associated with the token, or None if the token is invalid or the user does not exist.
    """
    payload = decode_token(token)
    if not payload:
        return None

    user_id = payload.get("id")
    if not user_id:
        return None

    return UserRepository(session).get_by_id(user_id)