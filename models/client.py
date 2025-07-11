from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Client(Base):
    """
        Represents an Epic Events client.

        Relationships:
            - Many-to-one with User: a client is managed by one commercial user.
            - One-to-many with Contract: a client has multiple contracts.


    Attributes:
        id (int): Primary key identifier for the client.
        fullname (str): Full name of the client. Required, max 70 characters.
        email (str): Unique email address of the client. Required, max 100 characters.
        phone (str, optional): Contact phone number. Optional, max 20 characters.
        company (str, optional): Company name. Optional, max 120 characters.
        created_at (datetime): Timestamp when the client was created.
        updated_at (datetime): Timestamp when the client was last updated.
        commercial_id (int, optional): Foreign key to the User who is the commercial contact.
        contracts (List[Contract]): List of contracts associated with this client.
        commercial (Optional[User]): The commercial user responsible for this client.
    """

    __tablename__ = "client"

    id: Mapped[int] = mapped_column(primary_key=True)
    fullname: Mapped[str] = mapped_column(String(70), nullable=False)
    email: Mapped[str] = mapped_column(
        String(100), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    company: Mapped[str] = mapped_column(String(120), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, nullable=False
    )

    commercial_id: Mapped[int] = mapped_column(
        ForeignKey("user_account.id"),
        nullable=True
    )

    # Relationships
    contracts: Mapped[List["Contract"]] = relationship(
        back_populates="client",
        cascade="all, delete-orphan"
    )
    commercial: Mapped[Optional["User"]] = relationship(
        back_populates="clients"
    )

    def __repr__(self) -> str:
        """Return a string representation of the Client instance.

        Returns:
            str: A string containing the client's ID, fullname, email, and company.
        """
        return (
            f"Client(id={self.id}, "
            f"fullname={self.fullname!r}, "
            f"email={self.email!r}, "
            f"company={self.company!r})"
        )
