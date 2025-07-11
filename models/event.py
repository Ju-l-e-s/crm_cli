from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Event(Base):
    """
        Represents an event associated with a contract.

        Relationships:
            - Many-to-one with Contract: each event belongs to one contract.
            - Many-to-one with User: each event can have one support contact (optional).

    Attributes:
        id (int): Primary key identifier for the event.
        name (str): Name of the event. Required, max 100 characters.
        start_date (datetime): Date and time when the event starts. Required.
        end_date (datetime): Date and time when the event ends. Required.
        location (str): Location of the event. Required, max 255 characters.
        attendees (int): Number of attendees expected at the event. Required.
        notes (str, optional): Additional notes about the event. Optional.
        contract_id (int): Foreign key to the Contract associated with this event. Required.
        support_contact_id (int, optional): Foreign key to the User (support) assigned to this event. Optional.
        contract (Contract): The contract associated with this event.
        support_contact (Optional[User]): The support user assigned to this event, if any.
    """

    __tablename__ = "event"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    attendees: Mapped[int] = mapped_column(nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Foreign keys
    contract_id: Mapped[int] = mapped_column(
        ForeignKey("contract.id"),
        nullable=False
    )
    support_contact_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("user_account.id")
    )

    # Relationships
    contract: Mapped["Contract"] = relationship(back_populates="events")
    support_contact: Mapped[Optional["User"]] = relationship(
        back_populates="events_support",
        foreign_keys=[support_contact_id]
    )

    def __repr__(self) -> str:
        """Return a string representation of the Event instance.

        Returns:
            str: A string containing the event's ID, name, start/end dates, 
                 location, number of attendees, and notes.
        """
        return (
            f"Event(id={self.id}, "
            f"name={self.name!r}, "
            f"start={self.start_date}, "
            f"end={self.end_date}, "
            f"location={self.location!r}, "
            f"attendees={self.attendees}, "
            f"notes={self.notes!r})"
        )
