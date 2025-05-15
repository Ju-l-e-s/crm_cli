import re
from models import UserRole

name_regex = re.compile(r"[A-Za-zÀ-ÿ \-']+")


def validate_name(name: str) -> str:
    name = name.strip()
    if not name:
        raise ValueError("Name cannot be empty.")
    if not re.fullmatch(name_regex, name):
        raise ValueError("Name must only contain letters, spaces, hyphens or apostrophes.")
    return name

email_regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')


def validate_email(email: str) -> str:
    email = email.strip().lower()
    if not re.fullmatch(email_regex, email):
        raise ValueError("Invalid email format.")
    return email

def validate_password(password: str) -> str:
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters.")
    if not re.search(r"[A-Z]", password):
        raise ValueError("Password must contain an uppercase letter.")
    if not re.search(r"[a-z]", password):
        raise ValueError("Password must contain a lowercase letter.")
    if not re.search(r"\d", password):
        raise ValueError("Password must contain a digit.")
    return password


def validate_role(role: str) -> UserRole:
    role_list = [r.value for r in UserRole]
    role = role.strip().lower()
    if role not in role_list:
        raise ValueError(f"Role must be one of: {', '.join(role_list)}")
    return UserRole(role)
