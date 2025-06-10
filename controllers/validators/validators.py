import re
from exceptions import CrmInvalidValue
from models.user_role import UserRole
from decimal import Decimal, InvalidOperation
from datetime import datetime, date

name_regex = re.compile(r"[A-Za-zÀ-ÿ \-']+")


def validate_name(name: str) -> str:
    name = name.strip()
    if not name:
        raise CrmInvalidValue("Name cannot be empty.")
    if not re.fullmatch(name_regex, name):
        raise CrmInvalidValue("Name must only contain letters, spaces, hyphens or apostrophes.")
    return name

email_regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')


def validate_email(email: str) -> str:
    email = email.strip().lower()
    if not re.fullmatch(email_regex, email):
        raise CrmInvalidValue("Invalid email format.")
    return email

def validate_password(password: str) -> str:
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
    role_list = [r.value for r in UserRole]
    role = role.strip().lower()
    if role not in role_list:
        raise CrmInvalidValue(f"Role must be one of: {', '.join(role_list)}")
    return UserRole(role)

def validate_phone(phone: str) -> str:
    phone = re.sub(r"[^\d+]", "", phone)  # remove all non-digit characters except "+"
    if not re.fullmatch(r"^\+?\d{7,15}$", phone):
        raise CrmInvalidValue("Invalid phone number format.")
    return phone

company_regex = re.compile(r"[A-Za-zÀ-ÿ0-9 &.,'\"°()\-]+")

def validate_company(name: str) -> str:
    name = name.strip()
    if not name:
        raise CrmInvalidValue("Company name cannot be empty.")
    if len(name) < 2:
        raise CrmInvalidValue("Company name is too short.")
    if not re.fullmatch(company_regex, name):
        raise CrmInvalidValue("Company name contains invalid characters.")
    return name

# Amount validator using Decimal
def validate_amount(amount) -> Decimal:
    try:
        dec = Decimal(str(amount))
    except (InvalidOperation, ValueError):
        raise CrmInvalidValue("Amount must be a valid decimal.")
    if dec <= 0:
        raise CrmInvalidValue("Amount must be greater than zero.")
    return dec

# Date validator
def validate_date(date_str: str) -> date:
    date_str = date_str.strip()
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise CrmInvalidValue("Date must be in format YYYY-MM-DD.")
    return dt