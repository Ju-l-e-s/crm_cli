from sqlalchemy import create_engine
from models.base import Base

from models.user import User
from models.client import Client
from models.contract import Contract
from models.event import Event

engine = create_engine("sqlite:///database/test.db", echo=True)
Base.metadata.create_all(engine)
print("️Database created successfully.")