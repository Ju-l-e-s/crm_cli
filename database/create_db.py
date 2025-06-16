import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.session import engine
from models.base import Base

from models.user import User
from models.client import Client
from models.contract import Contract
from models.event import Event

def create_database():
    print("Creating database and tables...")
    Base.metadata.create_all(bind=engine)
    print("Database and tables created successfully.")

if __name__ == "__main__":
    create_database()