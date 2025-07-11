from models.user_role import UserRole
from models.user import User
from models.event import Event
from models.contract import Contract
from models.client import Client
from models.base import Base
from database.session import SessionLocal, engine
import os
import sys
from datetime import datetime
from decimal import Decimal

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def seed_data() -> None:
    """Initialize the database with test data including users, clients, contracts, and events.

    This will drop all existing tables and recreate them with sample data.
    """
    print("Delete and recreate the database...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()

    print("Insert the test data...")
    # Create users
    commercial_1 = User(
        fullname="Lisa Simpson",
        email="lisa@test.com",
        role=UserRole.COMMERCIAL,
    )
    commercial_1.set_password("Azertyuiop123")

    commercial_2 = User(
        fullname="Marge Simpson",
        email="marge@test.com",
        role=UserRole.COMMERCIAL,
    )
    commercial_2.set_password("Azertyuiop123")

    gestion_1 = User(
        fullname="Homer Simpson",
        email="homer@test.com",
        role=UserRole.GESTION,
    )
    gestion_1.set_password("Azertyuiop123")

    gestion_2 = User(
        fullname="Abram Simpson",
        email="abram@test.com",
        role=UserRole.GESTION,
    )
    gestion_2.set_password("Azertyuiop123")

    support_1 = User(
        fullname="Bart Simpson",
        email="bart@test.com",
        role=UserRole.SUPPORT,
    )
    support_1.set_password("Azertyuiop123")

    support_2 = User(
        fullname="Maggie Simpson",
        email="maggie@test.com",
        role=UserRole.SUPPORT,
    )
    support_2.set_password("Azertyuiop123")

    session.add_all([commercial_1, commercial_2, gestion_1,
                    gestion_2, support_1, support_2])
    session.flush()  # Get user IDs

    # Create client
    client1 = Client(
        fullname="Selma Bouvier ",
        email="selma@startup.io",
        phone="+67812345678",
        company="Cool Startup LLC",
        commercial_id=commercial_1.id,
    )
    session.add(client1)
    session.flush()

    client2 = Client(
        fullname="Patty Bouvier",
        email="patty@startup.io",
        phone="+67812345644",
        company="Smocking Company",
        commercial_id=commercial_2.id,
    )
    session.add(client2)
    session.flush()

    # Create contract
    contract1 = Contract(
        total_amount=Decimal("900"),
        remaining_amount=Decimal("225"),
        end_date=datetime(2025, 12, 31),
        is_signed=True,
        client_id=client1.id,
        commercial_id=commercial_1.id,
    )
    session.add(contract1)
    session.flush()

    contract2 = Contract(
        total_amount=Decimal("1000"),
        remaining_amount=Decimal("250"),
        end_date=datetime(2025, 12, 31),
        is_signed=True,
        client_id=client2.id,
        commercial_id=commercial_2.id,
    )
    session.add(contract2)
    session.flush()

    # Create event
    event1 = Event(
        name="Family Party",
        start_date=datetime(2025, 6, 4, 13, 15),
        end_date=datetime(2025, 6, 5, 2),
        location="741 Evergreen Terrace, Springfield",
        attendees=75,
        notes=(
            "Family party for the Simpsons family. "
            "Catering is organized, reception starts at 5PM. "
            "Bart needs to organize the DJ for after party."
        ),
        contract_id=contract1.id,
        support_contact_id=support_1.id,
    )
    session.add(event1)

    event2 = Event(
        name="Patty's Wedding",
        start_date=datetime(2025, 6, 4, 13, 15),
        end_date=datetime(2025, 6, 5, 2),
        location="741 Evergreen Terrace, Springfield",
        attendees=75,
        notes=(
            "Wedding of Patty Bouvier. "
            "Catering is organized, reception starts at 5PM. "
            "Bart needs to organize the DJ for after party."
        ),
        contract_id=contract2.id,
        support_contact_id=support_2.id,
    )
    session.add(event2)

    session.commit()
    print("Test data inserted successfully.")

    session.close()


if __name__ == "__main__":
    seed_data()
