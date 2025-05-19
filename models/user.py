from typing import List
from sqlalchemy import String, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

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
        fullname (str): Full name of the user.
        email (str): Unique email address.
        role (UserRole): User role (commercial, support, or gestion).
        password_hash (str): Hashed password of the user.
        clients (List[Client]): Clients managed by the commercial user.
        events_support (List[Event]): Events the user supports.
    """
    __tablename__ = "user_account"

    id: Mapped[int] = mapped_column(primary_key=True)
    fullname: Mapped[str] = mapped_column(String(70), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    events_support: Mapped[List["Event"]] = relationship(back_populates="support_contact", cascade="all, delete-orphan")
    clients: Mapped[List["Client"]] = relationship(back_populates="commercial")

    def __repr__(self) -> str:
        return f"User(id={self.id}, fullname={self.fullname!r}, email={self.email!r}, role={self.role})"

    def set_password(self, password: str) -> None:
        self.password_hash = pass_hasher.hash(password)

    def check_password(self, password: str) -> bool:
        try:
            return pass_hasher.verify(self.password_hash, password)
        except VerifyMismatchError:
            return False
