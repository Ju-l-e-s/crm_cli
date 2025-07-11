import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from models.user_role import UserRole
from exceptions import CrmInvalidValue

# Regex patterns
name_regex = re.compile(r"[A-Za-zÀ-ÿ \-']+")
email_regex = re.compile(
    r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
company_regex = re.compile(r"[A-Za-zÀ-ÿ0-9 &.,'\"°()\-]+")


def validate_name(name: str) -> str:
    """
    Validate a person's name.

    Args:
        name (str): The name to validate.

    Returns:
        str: The validated and stripped name.

    Raises:
        CrmInvalidValue: If the name is empty or contains invalid characters.
    """
    name = name.strip()
    if not name:
        raise CrmInvalidValue("Name cannot be empty.")
    if not re.fullmatch(name_regex, name):
        raise CrmInvalidValue(
            "Name must only contain letters, spaces, hyphens or apostrophes."
        )
    return name


def validate_email(email: str) -> str:
    """
    Validate an email address.

    Args:
        email (str): The email address to validate.

    Returns:
        str: The validated and normalized email address in lowercase.

    Raises:
        CrmInvalidValue: If the email format is invalid.
    """
    email = email.strip().lower()
    if not re.fullmatch(email_regex, email):
        raise CrmInvalidValue("Invalid email format.")
    return email


def validate_password(password: str) -> str:
    """
    Validate a password against security requirements.

    Args:
        password (str): The password to validate.

    Returns:
        str: The validated password.

    Raises:
        CrmInvalidValue: If the password doesn't meet the requirements.
    """
    if len(password) < 8:
        raise CrmInvalidValue("Password must be at least 8 characters.")
    if not re.search(r"[A-Z]", password):
        raise CrmInvalidValue("Password must contain an uppercase letter.")
    if not re.search(r"[a-z]", password):
        raise CrmInvalidValue("Password must contain a lowercase letter.")
    if not re.search(r"\d", password):
        raise CrmInvalidValue("Password must contain a digit.")
    return password


def validate_role(role: str) -> UserRole:
    """
    Validate and convert a role string to a UserRole enum.

    Args:
        role (str): The role to validate.

    Returns:
        UserRole: The validated UserRole enum value.

    Raises:
        CrmInvalidValue: If the role is not one of the allowed values.
    """
    role_list = [r.value for r in UserRole]
    role = role.strip().lower()
    if role not in role_list:
        raise CrmInvalidValue(f"Role must be one of: {', '.join(role_list)}")
    return UserRole(role)


def validate_phone(phone: str) -> str:
    """
    Validate and normalize a phone number.

    Args:
        phone (str): The phone number to validate.

    Returns:
        str: The validated and normalized phone number.

    Raises:
        CrmInvalidValue: If the phone number format is invalid.
    """
    phone = re.sub(
        r"[^\d+]", "", phone)  # remove all non-digit characters except "+"
    if not re.fullmatch(r"^\+?\d{7,15}$", phone):
        raise CrmInvalidValue("Invalid phone number format.")
    return phone


def validate_company(name: str) -> str:
    """
    Validate a company name.

    Args:
        name (str): The company name to validate.

    Returns:
        str: The validated and stripped company name.

    Raises:
        CrmInvalidValue: If the company name is empty, too short, or contains invalid characters.
    """
    name = name.strip()
    if not name:
        raise CrmInvalidValue("Company name cannot be empty.")
    if len(name) < 2:
        raise CrmInvalidValue("Company name is too short.")
    if not re.fullmatch(company_regex, name):
        raise CrmInvalidValue("Company name contains invalid characters.")
    return name


def validate_amount(amount) -> Decimal:
    """
    Validate and convert an amount to a Decimal.

    Args:
        amount: The amount to validate (can be string, int, float, or Decimal).

    Returns:
        Decimal: The validated amount as a Decimal.

    Raises:
        CrmInvalidValue: If the amount is not a valid number or is not positive.
    """
    try:
        dec = Decimal(str(amount))
    except (InvalidOperation, ValueError):
        raise CrmInvalidValue("Amount must be a valid decimal.")
    if dec <= 0:
        raise CrmInvalidValue("Amount must be greater than zero.")
    return dec


def validate_date(date_str: str) -> date:
    """
    Validate and convert a date string to a date object.

    Args:
        date_str (str): The date string to validate (format: YYYY-MM-DD).

    Returns:
        date: The validated date object.

    Raises:
        CrmInvalidValue: If the date format is invalid.
    """
    date_str = date_str.strip()
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise CrmInvalidValue("Date must be in format YYYY-MM-DD.")
    return dt


def validate_event_name(name: str) -> str:
    """
    Validate an event name.

    Args:
        name (str): The event name to validate.

    Returns:
        str: The validated and stripped event name.

    Raises:
        CrmInvalidValue: If the event name is empty, too short, or contains invalid characters.
    """
    name = name.strip()
    if not name:
        raise CrmInvalidValue("Event name cannot be empty.")
    if len(name) < 3:
        raise CrmInvalidValue("Event name is too short.")
    if not re.fullmatch(r"[A-Za-zÀ-ÿ0-9 \-']+", name):
        raise CrmInvalidValue("Event name contains invalid characters.")
    return name


def validate_location(location: str) -> str:
    """
    Validate an event location.

    Args:
        location (str): The location to validate.

    Returns:
        str: The validated and stripped location.

    Raises:
        CrmInvalidValue: If the location is empty or too short.
    """
    location = location.strip()
    if not location:
        raise CrmInvalidValue("Location cannot be empty.")
    if len(location) < 3:
        raise CrmInvalidValue("Location is too short.")
    return location


def validate_attendees(attendees: int) -> int:
    """
    Validate the number of attendees.

    Args:
        attendees (int): The number of attendees to validate.

    Returns:
        int: The validated number of attendees.

    Raises:
        CrmInvalidValue: If the number of attendees is not a positive integer.
    """
    if not isinstance(attendees, int) or attendees < 1:
        raise CrmInvalidValue(
            "Number of attendees must be a positive integer.")
    return attendees


def validate_event_dates(start_date: str, end_date: str) -> tuple[datetime, datetime]:
    """
    Validate event start and end dates.

    Args:
        start_date (str): The start date string (format: YYYY-MM-DD HH:MM).
        end_date (str): The end date string (format: YYYY-MM-DD HH:MM).

    Returns:
        tuple[datetime, datetime]: A tuple of (start_datetime, end_datetime).

    Raises:
        CrmInvalidValue: If the date format is invalid or end date is not after start date.
    """
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d %H:%M")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d %H:%M")
    except ValueError:
        raise CrmInvalidValue("Invalid date format. Use YYYY-MM-DD HH:MM.")
    if end_dt <= start_dt:
        raise CrmInvalidValue("End date must be after start date.")
    return start_dt, end_dt
