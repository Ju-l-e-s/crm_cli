from functools import wraps

from sqlalchemy.orm import InstrumentedAttribute

from controllers.repositories.client_repository import ClientRepository
from controllers.repositories.contract_repository import ContractRepository
from controllers.repositories.event_repository import EventRepository
from controllers.services.auth import decode_token
from controllers.services.token_cache import load_token
from exceptions import (
    CrmAuthenticationError,
    CrmForbiddenAccessError,
    CrmInvalidValue,
    CrmNotFoundError,
)


def get_token_payload_or_raise() -> dict:
    """
    Load and decode the authentication token from cache.

    Returns:
        dict: The decoded token payload.

    Raises:
        CrmAuthenticationError: If the token is missing or invalid.
    """
    token = load_token()
    if not token:
        raise CrmAuthenticationError()
    return decode_token(token)


def get_client_owner_id(session, **kwargs) -> int:
    """
    Retrieve the commercial owner's ID for a client.

    Args:
        session: Database session or controller object with a session attribute.
        **kwargs: Must contain 'client_id'.

    Returns:
        int: The ID of the commercial owner.

    Raises:
        CrmNotFoundError: If the client does not exist.
    """
    if hasattr(session, 'session'):
        session = session.session
    client = ClientRepository(session).get_by_id(kwargs["client_id"])
    if not client:
        raise CrmNotFoundError("Client")
    return client.commercial_id


def get_contract_owner_id(session, contract_id: int) -> InstrumentedAttribute[int] | None:
    """
    Retrieve the commercial owner's ID for a contract.

    Args:
        session: Database session or controller object with a session attribute.
        contract_id (int): The ID of the contract.

    Returns:
        InstrumentedAttribute[int] | None: The ID of the commercial owner.

    Raises:
        CrmNotFoundError: If the contract does not exist.
    """
    if hasattr(session, 'session'):
        session = session.session
    contract = ContractRepository(session).get_by_id(contract_id)
    if not contract:
        raise CrmNotFoundError("Contract")
    return contract.commercial_id


def get_event_owner_id(session, event_id: int) -> int:
    """
    Retrieve the commercial owner's ID for an event via the linked contract.

    Args:
        session: Database session or controller object with a session attribute.
        event_id (int): The ID of the event.

    Returns:
        int: The ID of the commercial owner.

    Raises:
        CrmNotFoundError: If the event or its associated contract does not exist.
    """
    if hasattr(session, 'session'):
        session = session.session
    event = EventRepository(session).get_by_id(event_id)
    if not event:
        raise CrmNotFoundError("Event")
    contract = ContractRepository(session).get_by_id(event.contract_id)
    if not contract:
        raise CrmNotFoundError("Associated contract")
    return contract.commercial_id


def requires_role(required_role: str):
    """
    Decorator to restrict access to users with a specific role.

    Args:
        required_role (str): The role required to access the decorated function.

    Returns:
        function: The decorated function with role-based access control.
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

    Args:
        required_role (str): The role that can access any user's data.

    Returns:
        function: The decorated function with access control.
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

    Args:
        get_owner_id (function): Function that retrieves the owner ID of the resource.
        required_role (str): The role that can access any resource.

    Returns:
        function: The decorated function with ownership/role-based access control.

    Raises:
        CrmInvalidValue: If session is not provided.
        CrmForbiddenAccessError: If user lacks required role or ownership.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            session = kwargs.get("session")
            if session is None and args:
                session = args[0]
            if session is None:
                raise CrmInvalidValue("Session required")

            payload = get_token_payload_or_raise()
            current_user_id = payload["id"]
            current_user_role = payload["role"]

            if current_user_role == required_role:
                return func(*args, **kwargs)

            owner_kwargs = {'session': session}
            if 'client_id' in kwargs:
                owner_kwargs['client_id'] = kwargs['client_id']
            elif 'contract_id' in kwargs:
                owner_kwargs['contract_id'] = kwargs['contract_id']

            owner_id = get_owner_id(**owner_kwargs)
            if owner_id != current_user_id:
                raise CrmForbiddenAccessError

            return func(*args, **kwargs)
        return wrapper
    return decorator
