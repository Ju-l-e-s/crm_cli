from exceptions import CrmInvalidValue
from controllers.services.auth import decode_token
from controllers.services.token_cache import load_token
from functools import wraps


def requires_role(required_role: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args,**kwargs):
            token = load_token()
            if not token:
                raise CrmInvalidValue("Authentication required")
            payload = decode_token(token)
            if payload.get("role") != required_role:
                raise CrmInvalidValue("Forbidden")
            return func(*args,**kwargs)
        return wrapper
    return decorator

def requires_self_or_role(required_role: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            token = load_token()
            if not token:
                raise CrmInvalidValue("Authentication required")
            payload = decode_token(token)
            if payload["role"] != required_role and payload["id"] != kwargs["user_id"]:
                raise CrmInvalidValue("Forbidden")
            return func(*args, **kwargs)

        return wrapper

    return decorator
