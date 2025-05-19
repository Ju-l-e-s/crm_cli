from sqlalchemy import String, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional

from .base import Base

class Event(Base):
    """
        Represents an event associated with a contract.

        Relationships:
            - Many-to-one with Contract: each event belongs to one contract.
            - Many-to-one with User: each event can have one support contact (optional).

        Attributes:
            name (str): Name of the event.
            start_date (datetime): Date and time of the event start.
            end_date (datetime): Date and time of the event end.
            location (str): Location of the event.
            attendees (int): Number of attendees.
            notes (str): Notes about the event.
            contract_id (int): ID of the contract.
            contract (Contract): Contract associated with the event.
            support_contact_id (int): ID of the support contact.
            support_contact (User): User who supports the event.
    """
    __tablename__ = "event"

    id:   Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_date:   Mapped[datetime] = mapped_column(DateTime, nullable=False)

    location:  Mapped[str]           = mapped_column(String(255), nullable=False)
    attendees: Mapped[int]           = mapped_column(nullable=False)
    notes:     Mapped[Optional[str]] = mapped_column(Text)

    # FK
    contract_id: Mapped[int] = mapped_column(ForeignKey("contract.id"), nullable=False)
    support_contact_id: Mapped[Optional[int]] = mapped_column(ForeignKey("user_account.id"))

    # Relations
    contract:        Mapped["Contract"]       = relationship(back_populates="events")
    support_contact: Mapped[Optional["User"]] = relationship(back_populates="events_support", foreign_keys=[support_contact_id])

    def __repr__(self) -> str:
        return f"Event(id={self.id}, name={self.name!r}, start={self.start_date}, end={self.end_date}, location={self.location!r}, attendees={self.attendees}, notes={self.notes!r})"