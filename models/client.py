from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import List, Optional

from .base import Base

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
    phone:      Mapped[str] = mapped_column(String(20),nullable=True)
    company:    Mapped[str] = mapped_column(String(120),nullable=True)

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