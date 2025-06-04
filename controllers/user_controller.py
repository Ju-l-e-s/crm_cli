from typing import Type

from sqlalchemy.orm import Session
from exceptions import CrmInvalidValue
from models.user import User
from controllers.repositories.user_repository import UserRepository
from controllers.validators.user_validators import validate_name, validate_email, validate_password, validate_role
from controllers.services.auth import generate_token
from controllers.services.token_cache import save_token


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
            return UserRepository(self.session).save(user)
        except Exception as e:
            raise CrmInvalidValue(f"Could not create user: {e}") from e

    def authenticate(self, email: str, password: str) -> User:
        """
        Authenticates a user based on email and password, stores JWT in cache.

        :param email: The email of the user to authenticate.
        :param password: The password of the user to authenticate.
        :return: The authenticated user.
        :raises CrmInvalidValue: If the user is not found or password is incorrect.
        """
        user = UserRepository(self.session).get_by_email(email)
        if not user:
            raise CrmInvalidValue("User not found.")

        if not user.check_password(password):
            raise CrmInvalidValue("Wrong password.")

        token = generate_token(user)
        save_token(token)
        return user

    # @requires_role("gestion")
    def list_all_users(self) -> list[Type[User]]:
        """
        Lists all users. Only 'gestion' can list all users.
        """
        return UserRepository(self.session).list_all()

    def get_user_by_id(self, user_id: int) -> User:
        """
        Retrieves a single user by ID.
        :raises CrmInvalidValue: If user does not exist.
        """
        user = UserRepository(self.session).get_by_id(user_id)
        if not user:
            raise CrmInvalidValue("User not found.")
        return user

    # @requires_self_or_role("gestion")
    def update_user(self, user_id: int, fullname: str, email: str, role: str) -> User:
        """
        Updates a user's information. A user can update his own profile, or a 'gestion' can update any.
        """
        user = UserRepository(self.session).get_by_id(user_id)
        if not user:
            raise CrmInvalidValue("User not found.")

        fullname = validate_name(fullname)
        email = validate_email(email)
        role = validate_role(role)

        user.fullname = fullname
        user.email = email
        user.role = role

        try:
            return UserRepository(self.session).save(user)
        except Exception as e:
            raise CrmInvalidValue(f"Could not update user: {e}") from e