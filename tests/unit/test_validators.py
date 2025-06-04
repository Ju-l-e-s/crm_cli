import pytest

from exceptions import CrmInvalidValue
from controllers.validators.user_validators import (
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




