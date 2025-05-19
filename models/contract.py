from sqlalchemy import DateTime, ForeignKey, Numeric, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import List
from decimal import Decimal

from .base import Base

class Contract(Base):
    """
        Represents a contract between a client and an Epic Events employee.

        Relationships:
            - Many-to-one with Client: a contract is linked to one client.
            - One-to-many with Event: a contract can include multiple events.

        Attributes:
            total_amount (Decimal): Total amount of the contract.
            remaining_amount (Decimal): Remaining amount of the contract.
            creation_date (datetime): Date and time of creation.
            end_date (datetime): Date and time of the contract end.
            is_signed (bool): Whether the contract has been signed.
            client_id (int): ID of the client.
            client (Client): Client associated with the contract.
            events (List[Event]): Events associated with the contract.
    """
    __tablename__ = "contract"

    id:               Mapped[int]      = mapped_column(primary_key=True)
    total_amount:     Mapped[Decimal]  = mapped_column(Numeric(12, 2), nullable=False)
    remaining_amount: Mapped[Decimal]  = mapped_column(Numeric(12, 2), nullable=False)
    creation_date:    Mapped[datetime] = mapped_column( DateTime, default=datetime.now, nullable=False)
    end_date:         Mapped[datetime] = mapped_column(DateTime)
    is_signed:        Mapped[bool]     = mapped_column(Boolean, default=False, nullable=False)

    # FK
    client_id:        Mapped[int]      = mapped_column(ForeignKey("client.id"), nullable=False)

    # Relations
    client:           Mapped["Client"]      = relationship(back_populates="contracts")
    events:           Mapped[List["Event"]] = relationship(back_populates="contract",cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"Contract(id={self.id}, total={self.total_amount!r}, remaining={self.remaining_amount}, creation={self.creation_date}, end={self.end_date}, signed={self.is_signed})"