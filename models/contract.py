from datetime import datetime
from decimal import Decimal
from typing import List

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Contract(Base):
    """
        Represents a contract between a client and an Epic Events employee.

        Relationships:
            - Many-to-one with Client: a contract is linked to one client.
            - One-to-many with Event: a contract can include multiple events.

    Attributes:
        id (int): Primary key identifier for the contract.
        total_amount (Decimal): Total amount of the contract. Required, max 12 digits with 2 decimal places.
        remaining_amount (Decimal): Remaining amount to be paid. Required, max 12 digits with 2 decimal places.
        creation_date (datetime): Timestamp when the contract was created. Automatically set to current time.
        end_date (datetime): Date and time when the contract ends. Required.
        is_signed (bool): Whether the contract has been signed. Defaults to False.
        client_id (int): Foreign key to the Client associated with this contract. Required.
        commercial_id (int): Foreign key to the User (commercial) responsible for this contract. Required.
        client (Client): The client associated with this contract.
        events (List[Event]): List of events associated with this contract.
        commercial (User): The commercial user responsible for this contract.
    """

    __tablename__ = "contract"

    id: Mapped[int] = mapped_column(primary_key=True)
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )
    remaining_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )
    creation_date: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False
    )
    end_date: Mapped[datetime] = mapped_column(DateTime)
    is_signed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    # Foreign keys
    client_id: Mapped[int] = mapped_column(
        ForeignKey("client.id"),
        nullable=False
    )
    commercial_id: Mapped[int] = mapped_column(
        ForeignKey("user_account.id"),
        nullable=False
    )

    # Relationships
    client: Mapped["Client"] = relationship(back_populates="contracts")
    events: Mapped[List["Event"]] = relationship(
        back_populates="contract",
        cascade="all, delete-orphan"
    )
    commercial: Mapped["User"] = relationship(back_populates="contracts")

    def __repr__(self) -> str:
        """Return a string representation of the Contract instance.

        Returns:
            str: A string containing the contract's ID, amounts, creation date, 
                 end date, and signed status.
        """
        return (
            f"Contract(id={self.id}, "
            f"total={self.total_amount!r}, "
            f"remaining={self.remaining_amount}, "
            f"creation={self.creation_date}, "
            f"end={self.end_date}, "
            f"signed={self.is_signed})"
        )
