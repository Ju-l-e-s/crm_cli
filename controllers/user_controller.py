from sqlalchemy.orm import Session
from database.create_db import engine
from models.user import User
from validators.user_validators import validate_name, validate_email, validate_password, validate_role

class UserController:
    def __init__(self, session: Session):
        self.session = session

    def create_user(self, fullname: str, email: str, role: str, password: str) -> User:
        """
        Creates a new user in the database.

        :param fullname: The user's full name.
        :param email: The user's email address.
        :param role: The user's role.
        :param password: The user's password.
        :return: The created user.

        """
        fullname = validate_name(fullname)
        email = validate_email(email)
        password = validate_password(password)
        role = validate_role(role)

        user = User(fullname=fullname, email=email, role=role)
        user.set_password(password)

        try:
            self.session.add(user)
            self.session.commit()
            self.session.refresh(user)
            return user
        except Exception as e:
            self.session.rollback()
            raise ValueError(f"Could not create user: {e}") from e
    def authenticate(self, email: str, password: str) -> User:
        """
        Authenticates a user based on email and password.

        :param email: The email of the user to authenticate.
        :param password: The password of the user to authenticate.
        :return: The authenticated user.
        :raises ValueError: If the user is not found or if the password is incorrect.
        """
        user = self.session.query(User).filter(User.email == email).first()
        if not user:
            raise ValueError("User not found.")

        if not user.check_password(password):
            raise ValueError("Wrong password.")

        return user

if __name__ == "__main__":
    with Session(engine) as session:
        controller = UserController(session)
        test_user = controller.create_user(
            fullname="Nicolas Pin",
            email="nicolas2@epicenvents.com",
            role="support",
            password="TopSecret123"
        )
        print(f"User created: {test_user}")