from functools import wraps

from sqlalchemy.orm import InstrumentedAttribute

from controllers.repositories.client_repository import ClientRepository
from controllers.repositories.contract_repository import ContractRepository
from controllers.repositories.event_repository import EventRepository
from controllers.services.auth import decode_token
from controllers.services.token_cache import load_token
from exceptions import CrmInvalidValue, CrmForbiddenAccessError


# --- Utility functions ---

def get_token_payload_or_raise() -> dict:
    """
    Loads the token from cache and decodes it.
    Raises an exception if the token is missing or invalid.
    """
    token = load_token()
    if not token:
        raise CrmInvalidValue("Authentication required")
    return decode_token(token)

def get_client_owner_id(session, **kwargs):
    """
    Retrieves the commercial owner's ID for a client.
    Raises an exception if the client does not exist.
    """
    client = ClientRepository(session).get_by_id(kwargs["client_id"])
    if not client:
        raise CrmInvalidValue("Client not found.")
    return client.commercial_id

def get_contract_owner_id(session, contract_id: int) -> InstrumentedAttribute[int] | None:
    """
    Retrieves the commercial owner's ID for a contract.
    Raises an exception if the contract does not exist.
    """
    contract = ContractRepository(session).get_by_id(contract_id)
    if not contract:
        raise CrmInvalidValue("Contract not found.")
    return contract.commercial_id

def get_event_owner_id(session, event_id: int):
    """
    Retrieves the commercial owner's ID for an event (via the linked contract).
    Raises an exception if the event or its associated contract does not exist.
    """
    event = EventRepository(session).get_by_id(event_id)
    if not event:
        raise CrmInvalidValue("Event not found.")
    # Retrieve the commercial via the contract linked to the event
    contract = ContractRepository(session).get_by_id(event.contract_id)
    if not contract:
        raise CrmInvalidValue("Associated contract not found.")
    return contract.commercial_id

# --- Permission decorators ---

def requires_role(required_role: str):
    """
    Decorator to restrict access to users with a specific role.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            payload = get_token_payload_or_raise()
            if payload.get("role") != required_role:
                raise CrmForbiddenAccessError
            return func(*args, **kwargs)
        return wrapper
    return decorator

def requires_self_or_role(required_role: str):
    """
    Decorator to restrict access to the user themselves or users with a specific role.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            payload = get_token_payload_or_raise()
            if payload["role"] != required_role and payload["id"] != kwargs.get("user_id"):
                raise CrmForbiddenAccessError
            return func(*args, **kwargs)
        return wrapper
    return decorator

def requires_ownership_or_role(get_owner_id, required_role: str):
    """
    Decorator to restrict access to the resource owner or users with a specific role.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Try to extract the session from kwargs or positional args
            session = kwargs.get("session")
            if session is None and args:
                session = args[0]
            if session is None:
                raise CrmInvalidValue("Session required")

            payload = get_token_payload_or_raise()
            current_user_id = payload["id"]
            current_user_role = payload["role"]

            # Allow if user has the required role
            if current_user_role == required_role:
                return func(*args, **kwargs)

            # Otherwise, check resource ownership
            owner_id = get_owner_id(session, **kwargs)
            if owner_id != current_user_id:
                raise CrmForbiddenAccessError

            return func(*args, **kwargs)
        return wrapper
    return decorator