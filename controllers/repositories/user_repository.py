from typing import Type

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.user import User


class UserRepository:
    """
    Repository class for handling database operations for User model.
    """

    def __init__(self, session: Session):
        """
        Initialize the UserRepository with a database session.

        Args:
            session (Session): SQLAlchemy database session.
        """
        self.session = session

    def get_by_email(self, email: str) -> User | None:
        """
        Retrieve a user by their email address.

        Args:
            email (str): The email address of the user to retrieve.

        Returns:
            User | None: The User object if found, None otherwise.
        """
        return self.session.query(User).filter_by(email=email).first()

    def get_by_id(self, user_id: int) -> User | None:
        """
        Retrieve a user by their ID.

        Args:
            user_id (int): The ID of the user to retrieve.

        Returns:
            User | None: The User object if found, None otherwise.
        """
        return self.session.query(User).filter_by(id=user_id).first()

    def save(self, user: User) -> User:
        """
        Save a user to the database.

        Args:
            user (User): The User object to save.

        Returns:
            User: The saved User object with updated attributes.

        Raises:
            IntegrityError: If there is a database integrity error.
        """
        try:
            self.session.add(user)
            self.session.commit()
            self.session.refresh(user)
            return user
        except IntegrityError:
            self.session.rollback()
            raise

    def delete(self, user: User) -> None:
        """
        Delete a user from the database.

        Args:
            user (User): The User object to delete.

        Raises:
            IntegrityError: If there is a database integrity error.
        """
        try:
            self.session.delete(user)
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise

    def list_all(self) -> list[Type[User]]:
        """
        Retrieve all users from the database.

        Returns:
            list[Type[User]]: A list of all User objects.
        """
        return self.session.query(User).all()
