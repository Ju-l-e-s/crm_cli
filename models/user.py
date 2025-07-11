from typing import List

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .user_role import UserRole

pass_hasher = PasswordHasher()


class User(Base):
    """
    Represents an Epic Events employee.

    Relationships:
        - One-to-many with Client: a commercial user manages multiple clients.
        - One-to-many with Event: a support user is assigned to multiple events.

    Attributes:
        id (int): Primary key identifier for the user.
        fullname (str): Full name of the user. Required, max 70 characters.
        email (str): Unique email address. Required, max 100 characters.
        role (UserRole): User role (commercial, support, or gestion). Required.
        password_hash (str): Hashed password using Argon2. Required, max 255 characters.
        events_support (List[Event]): List of events this user is supporting.
        clients (List[Client]): List of clients managed by this user (if commercial).
        contracts (List[Contract]): List of contracts managed by this user.
    """

    __tablename__ = "user_account"

    id: Mapped[int] = mapped_column(primary_key=True)
    fullname: Mapped[str] = mapped_column(String(70), nullable=False)
    email: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True
    )
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # Relationships
    events_support: Mapped[List["Event"]] = relationship(
        back_populates="support_contact"
    )
    clients: Mapped[List["Client"]] = relationship(
        back_populates="commercial"
    )
    contracts: Mapped[List["Contract"]] = relationship(
        back_populates="commercial"
    )

    def __repr__(self) -> str:
        """Return a string representation of the User instance.

        Returns:
            str: A string containing the user's ID, fullname, email, and role.
        """
        return (
            f"User(id={self.id}, "
            f"fullname={self.fullname!r}, "
            f"email={self.email!r}, "
            f"role={self.role})"
        )

    def set_password(self, password: str) -> None:
        """Set the user's password by hashing the provided plaintext password.

        Args:
            password (str): The plaintext password to hash and store.
        """
        self.password_hash = pass_hasher.hash(password)

    def check_password(self, password: str) -> bool:
        """Verify if the provided password matches the stored hash.

        Args:
            password (str): The plaintext password to verify.

        Returns:
            bool: True if the password matches, False otherwise.
        """
        try:
            return pass_hasher.verify(self.password_hash, password)
        except VerifyMismatchError:
            return False
