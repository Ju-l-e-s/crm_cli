import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Use a environment variable for the DB URL, with a default value
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///database/test.db")

# Create the database engine
engine = create_engine(DATABASE_URL, echo=False)

# Create a "factory" of sessions configured
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)