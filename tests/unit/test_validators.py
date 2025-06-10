import pytest

from exceptions import CrmInvalidValue
from datetime import date
from decimal import Decimal
from controllers.validators.validators import (
    validate_name,
    validate_email,
    validate_password,
    validate_role,
    validate_amount,
    validate_date,
    validate_event_name,
    validate_location,
    validate_attendees,
    validate_event_dates
)

# name
def test_validate_name_valid():
    assert validate_name("Sarah Croche") == "Sarah Croche"

def test_validate_name_empty():
    with pytest.raises(CrmInvalidValue):
        validate_name("")
#email
def test_validate_email_valid():
    assert validate_email("user@example.com") == "user@example.com"
def test_validate_email_invalid():
    with pytest.raises(CrmInvalidValue):
        validate_email("notanemail")
# password
def test_validate_password_valid():
    assert validate_password("StrongPass1") == "StrongPass1"
def test_validate_password_too_short():
    with pytest.raises(CrmInvalidValue):
        validate_password("abc")
def test_validate_password_no_uppercase():
    with pytest.raises(CrmInvalidValue):
        validate_password("weakpass1")
# role
def test_validate_role_valid():
    assert validate_role("support").value == "support"
def test_validate_role_invalid():
    with pytest.raises(CrmInvalidValue):
        validate_role("invalid")


import pytest
from controllers.validators.validators import validate_phone, validate_company
from exceptions import CrmInvalidValue

# phone

@pytest.mark.parametrize("valid_phone", [
    "+33612345678",
    "+1 234 567 8901",
    "0123456789",
    "+33 6 12 34 56 78",
    "+4917612345678",
])
def test_validate_phone_valid(valid_phone):
    result = validate_phone(valid_phone)
    assert isinstance(result, str)
    assert result.startswith("+") or result.isdigit()

@pytest.mark.parametrize("invalid_phone", [
    "abc123",  # letters
    "+33",     # too short
    "+12345678901234567",  # too long
    "",        # empty
    "++33612345678",  # double +
])
def test_validate_phone_invalid(invalid_phone):
    with pytest.raises(CrmInvalidValue):
        validate_phone(invalid_phone)

# company
@pytest.mark.parametrize("valid_name", [
    "Cool Startup LLC",
    "Monstres & Co.",
    "Entreprise-Test 42",
    "SARL L'altitude",
    "Compagnie Générale (France)",
])
def test_validate_company_name_valid(valid_name):
    result = validate_company(valid_name)
    assert isinstance(result, str)
    assert result == valid_name.strip()

@pytest.mark.parametrize("invalid_name", [
    "",          # empty
    "A",         # too short
    "   ",       # just spaces
    "😂 Company",  # emoji not allowed
])
def test_validate_company_name_invalid(invalid_name):
    with pytest.raises(CrmInvalidValue):
        validate_company(invalid_name)

#amount
@pytest.mark.parametrize("valid_amount", ["10",  "0.01", Decimal("99.99")])
def test_validate_amount_valid(valid_amount):
    dec = validate_amount(valid_amount)
    assert isinstance(dec, Decimal)
    assert dec > 0

@pytest.mark.parametrize("invalid_amount", ["abc", "-5", 0, -1])
def test_validate_amount_invalid(invalid_amount):
    with pytest.raises(CrmInvalidValue):
        validate_amount(invalid_amount)

# date
@pytest.mark.parametrize("valid_date", ["2025-06-09", "2000-01-01"])
def test_validate_date_valid(valid_date):
    d = validate_date(valid_date)
    assert isinstance(d, date)

@pytest.mark.parametrize("invalid_date", ["", "09-06-2025", "2025/06/09", "2025-13-01"])
def test_validate_date_invalid(invalid_date):
    with pytest.raises(CrmInvalidValue):
        validate_date(invalid_date)

# event name
def test_validate_event_name_ok():
    assert validate_event_name("Conférence 2025") == "Conférence 2025"

def test_validate_event_name_empty():
    with pytest.raises(CrmInvalidValue):
        validate_event_name("")

def test_validate_event_name_invalid():
    with pytest.raises(CrmInvalidValue):
        validate_event_name("@bad!")

def test_validate_location_ok():
    assert validate_location("Paris Expo") == "Paris Expo"

def test_validate_location_empty():
    with pytest.raises(CrmInvalidValue):
        validate_location("")

def test_validate_attendees_ok():
    assert validate_attendees(10) == 10

def test_validate_attendees_invalid():
    with pytest.raises(CrmInvalidValue):
        validate_attendees(0)
    with pytest.raises(CrmInvalidValue):
        validate_attendees(-5)

def test_validate_event_dates_ok():
    start, end = validate_event_dates("2025-06-10 09:00", "2025-06-10 18:00")
    assert start.hour == 9 and end.hour == 18

def test_validate_event_dates_invalid_format():
    with pytest.raises(CrmInvalidValue):
        validate_event_dates("2025-06-10", "2025-06-10 18:00")

def test_validate_event_dates_end_before_start():
    with pytest.raises(CrmInvalidValue):
        validate_event_dates("2025-06-10 18:00", "2025-06-10 09:00")
