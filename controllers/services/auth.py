import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from jwt import decode, encode, ExpiredSignatureError, InvalidTokenError
from sqlalchemy.orm import Session

from controllers.repositories.user_repository import UserRepository
from controllers.services.token_cache import delete_token, load_token
from exceptions import CrmAuthenticationError
from models.user import User

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_EXPIRES_IN = int(os.getenv("JWT_EXPIRES_IN", 3600 * 24))


def generate_token(user: User) -> str:
    """
    Generate a JWT token for a user.

    Args:
        user (User): The user to generate a token for.

    Returns:
        str: The generated JWT token.
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
    Decode a JWT token and return its payload.

    Args:
        token (str): The JWT token to decode.

    Returns:
        dict: The decoded token payload.

    Raises:
        CrmAuthenticationError: If the token is expired or invalid.
    """
    try:
        payload = decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except ExpiredSignatureError:
        delete_token()
        raise CrmAuthenticationError("Token expired.")
    except InvalidTokenError:
        delete_token()
        raise CrmAuthenticationError("Invalid token.")


def get_user_from_token(token: str, session: Session) -> User | None:
    """
    Retrieve a user from a JWT token.

    Args:
        token (str): The JWT token containing the user ID.
        session (Session): Database session for user lookup.

    Returns:
        User | None: The user if found and token is valid, None otherwise.
    """
    payload = decode_token(token)
    if not payload:
        return None

    user_id = payload.get("id")
    if not user_id:
        return None

    return UserRepository(session).get_by_id(user_id)


def get_current_user(session: Session) -> User | None:
    """
    Get the currently authenticated user from the stored token.

    Args:
        session (Session): Database session for user lookup.

    Returns:
        User | None: The authenticated user if valid token exists, None otherwise.

    Raises:
        CrmAuthenticationError: If no token is found or token is invalid.
    """
    token = load_token()
    if not token:
        raise CrmAuthenticationError("No authentication token found.")

    payload = decode_token(token)
    user_id = payload["id"]
    user = UserRepository(session).get_by_id(user_id)

    if not user:
        raise CrmAuthenticationError("User not found.")

    return user
