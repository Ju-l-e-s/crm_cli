from datetime import datetime
from decimal import Decimal
from typing import List, Optional

import enum
from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    String,
    Text
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship
)

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

pass_hasher = PasswordHasher()
# -------------------------------------------------------------------------
# 1. Base class for all models
# -------------------------------------------------------------------------
class Base(DeclarativeBase):
    pass

# -------------------------------------------------------------------------
# 2. Enum for roles
# -------------------------------------------------------------------------
class UserRole(enum.Enum):
    COMMERCIAL = "commercial"
    SUPPORT    = "support"
    GESTION    = "gestion"

# -------------------------------------------------------------------------
# 3. User model
# -------------------------------------------------------------------------
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
        clients (List[Client]): Clients managed by the commercial user.
        events_support (List[Event]): Events the user supports.
    """
    __tablename__ = "user_account"

    id:       Mapped[int]  = mapped_column(primary_key=True)
    fullname: Mapped[str]  = mapped_column(String(70),  nullable=False)
    email:    Mapped[str]  = mapped_column(String(100), nullable=False, unique=True)

    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # Relations
    events_support: Mapped[List["Event"]] = relationship(back_populates="support_contact", cascade="all, delete-orphan")
    clients: Mapped[List["Client"]] = relationship(back_populates="commercial")

    def __repr__(self) -> str:
        return f"User(id={self.id}, fullname={self.fullname!r}, email={self.email!r}, role={self.role})"

    def set_password(self, password: str) -> None:
        self.password_hash = pass_hasher.hash(password)

    def check_password(self, password: str) -> bool:
        try:
            return pass_hasher.verify(self.password_hash ,password)
        except VerifyMismatchError:
            return False

# -------------------------------------------------------------------------
# 4. Client model
# -------------------------------------------------------------------------
class Client(Base):
    """
        Represents an Epic Events client.

        Relationships:
            - Many-to-one with User: a client is managed by one commercial user.
            - One-to-many with Contract: a client has multiple contracts.


        Attributes:
            fullname (str): Full name of the client.
            email (str): Unique email address.
            phone (str): Phone number.
            company (str): Company name.
            created_at (datetime): Date and time of creation.
            updated_at (datetime): Date and time of last update.
            commercial_id (int): ID of the commercial user.
            contracts (List[Contract]): Contracts associated with the client.
    """
    __tablename__ = "client"

    id:         Mapped[int] = mapped_column(primary_key=True)
    fullname:   Mapped[str] = mapped_column(String(70), nullable=False)
    email:      Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    phone:      Mapped[str] = mapped_column(String(20))
    company:    Mapped[str] = mapped_column(String(120))

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

    commercial_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"), nullable=True)
    # Relations
    # 1-N : a client has one to many contracts
    contracts: Mapped[List["Contract"]] = relationship(back_populates="client", cascade="all, delete-orphan")

    # 1-N : a client has one user as commercial
    commercial: Mapped[Optional["User"]] = relationship(back_populates="clients")

    def __repr__(self) -> str:
        return f"Client(id={self.id}, fullname={self.fullname!r}, email={self.email!r}, company={self.company!r})"

# -------------------------------------------------------------------------
# 5 - Contract model
# -------------------------------------------------------------------------
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

# -------------------------------------------------------------------------
# 6 - Event model
# -------------------------------------------------------------------------
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