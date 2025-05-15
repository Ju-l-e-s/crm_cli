from sqlalchemy.orm import Session
from models import User
from validators import validate_name, validate_email, validate_role, validate_password

def create_user(session: Session, fullname: str, email: str, role: str, password: str) -> User:
    """
        Create a new user in the database and return the User instance.
        Args:
            session (Session): SQLAlchemy session object.
            fullname (str): Full name of the user.
            email (str): Unique email address.
            role (str): User role (commercial, support, or gestion).
            password (str): Password of the user.
        Returns:
            User: The created user.

    """
    fullname = validate_name(fullname)
    email = validate_email(email)
    password = validate_password(password)
    role = validate_role(role)

    user = User(fullname=fullname, email=email, role=role)
    user.set_password(password)

    try:
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    except Exception as e:
        session.rollback()
        raise ValueError(f"Could not create user: {e}") from e


from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from create_db import engine

if __name__ == "__main__":
    with Session(engine) as session:
        test_user = create_user(
            session,
            fullname="Nicolas Pin",
            email="nicolas@epicenvents.com",
            role="support",
            password="TopSecret123"
        )
        print(f"User created: {test_user}")