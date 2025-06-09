import pytest

from exceptions import CrmInvalidValue
from controllers.validators.validators import (
    validate_name,
    validate_email,
    validate_password,
    validate_role
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


