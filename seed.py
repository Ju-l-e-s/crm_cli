import os
import sys
from datetime import datetime
from decimal import Decimal

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.session import SessionLocal, engine
from models.base import Base
from models.user import User
from models.client import Client
from models.contract import Contract
from models.event import Event
from models.user_role import UserRole

def seed_data():
    # Recreate the database for a clean state
    print("Delete and recreate the database...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()

    try:
        print("Insertion des données de test...")
        # Create users
        user1 = User(
            fullname="Lisa Simpson",
            email="lisa@test.com",
            role=UserRole.COMMERCIAL,
        )
        user1.set_password("Azertyuiop123")

        user2 = User(
            fullname="Homer Simpson",
            email="homer@test.com",
            role=UserRole.GESTION,
        )
        user2.set_password("Azertyuiop123")

        user3 = User(
            fullname="Bart Simpson",
            email="bart@test.com",
            role=UserRole.SUPPORT,
        )
        user3.set_password("Azertyuiop123")

        session.add_all([user1, user2, user3])
        session.flush() # Get user IDs

        # Create client
        client1 = Client(
            fullname="Maggie Simpson",
            email="maggie@startup.io",
            phone="+67812345678",
            company="Cool Startup LLC",
            commercial_id=user1.id,
        )
        session.add(client1)
        session.flush() # Get client ID

        # Create contract
        contract1 = Contract(
            total_amount=Decimal("1000"),
            remaining_amount=Decimal("250"),
            end_date=datetime(2025, 12, 31),
            is_signed=True,
            client_id=client1.id,
            commercial_id=user1.id,
        )
        session.add(contract1)
        session.flush() # Pour obtenir l'ID du contrat

        # Create event
        event1 = Event(
            name="John Ouick Wedding",
            start_date=datetime(2025, 6, 4, 13, 15),
            end_date=datetime(2025, 6, 5, 2),
            location="742 Evergreen Terrace, Springfield",
            attendees=75,
            notes="Wedding starts at 3PM, by the river.Catering is organized, reception starts at 5PM. Bart needs to organize the DJ for after party.",
            contract_id=contract1.id,
            support_contact_id=user3.id,
        )
        session.add(event1)

        session.commit()
        print("Test data inserted successfully.")

    except Exception as e:
        print(f"An error occurred during seeding: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    seed_data()
