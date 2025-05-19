from sqlalchemy import create_engine

from models.user import User
from models.user_role import UserRole
from models.client import Client
from models.contract import Contract
from models.event import Event

from datetime import datetime
from decimal import Decimal

engine = create_engine("sqlite:///database/test.db", echo=True)

from sqlalchemy.orm import Session

with Session(engine) as session:
    # Create a new user
    user1 = User(
    fullname = "Alice O'paysdesmerveilles",
    email = "alice@epicenvents.com",
    role = UserRole.COMMERCIAL,
  )
    user1.set_password("TopSecret123")
    session.add(user1)

    # Create a new client
    client1 = Client(
        fullname = "Kevin Casey",
        email = "kevin@startup.io",
        phone = "+67812345678",
        company = "Cool Startup LLC",
        commercial = user1
    )
    session.add(client1)

    # Create a new contract
    contract1 = Contract(
        total_amount=Decimal("1000"),
        remaining_amount=Decimal("250"),
        end_date = datetime(2025,12,31),
        is_signed = True,
        client = client1
    )
    session.add(contract1)

    # Create a new event
    event1 = Event(
        name = "John Ouick Wedding",
        start_date = datetime(2025,6,4,13,15),
        end_date = datetime(2025,6,5,2),
        location = "53 Rue du Château, Candé-sur-Beuvron",
        attendees = 75,
        notes = "Wedding starts at 3PM, by the river.Catering is organized, reception starts at 5PM. Kate needs to organize the DJ for after party.",
        contract = contract1,
    )
    session.add(event1)

    # Commit
    session.commit()
    print ("Data inserted successfully!")
