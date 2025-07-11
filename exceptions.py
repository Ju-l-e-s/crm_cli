class CrmError(Exception):
    """Base class for all CRM errors."""
    pass


class CrmForbiddenAccessError(CrmError):
    """Raised when a user tries to access a forbidden resource."""

    def __init__(self, message=None):
        if message is None:
            message = "Forbidden: you do not have permission to access this resource."
        super().__init__(message)


class CrmInvalidValue(CrmError, ValueError):
    """Raised when a value is invalid (validation, parsing, etc)."""

    def __init__(self, message=None):
        if message is None:
            message = "Invalid value."
        super().__init__(message)


class CrmNotFoundError(CrmError):
    """Raised when a resource is not found."""

    def __init__(self, resource="Resource", message=None):
        if message is None:
            message = f"{resource} not found."
        super().__init__(message)


class CrmIntegrityError(CrmError):
    """Raised when there is a database integrity error."""

    def __init__(self, message=None):
        if message is None:
            message = "Integrity error."
        super().__init__(message)


class CrmAuthenticationError(CrmError):
    """Raised when authentication fails or is missing."""

    def __init__(self, message=None):
        if message is None:
            message = "Authentication required."
        super().__init__(message)
