# database.py

# -----------------------------------------------------
# Load Environment Variables
# -----------------------------------------------------

# Loads environment variables from the .env file
from dotenv import load_dotenv

# Reads environment variables from the operating system
import os

# -----------------------------------------------------
# SQLAlchemy Imports
# -----------------------------------------------------

# Creates the SQLAlchemy Engine
from sqlalchemy import create_engine

# Creates database sessions
from sqlalchemy.orm import sessionmaker

# Base class that every database model will inherit
from sqlalchemy.orm import DeclarativeBase


# -----------------------------------------------------
# Load .env
# -----------------------------------------------------

load_dotenv()


# -----------------------------------------------------
# Read Database URL
# -----------------------------------------------------
# Reads the PostgreSQL connection string
# from the .env file.
#
DATABASE_URL = os.getenv("DATABASE_URL")


# -----------------------------------------------------
# Create Database Engine
# -----------------------------------------------------
# The Engine is responsible for communicating
# with PostgreSQL.
#
# It knows:
# - Which database to connect to
# - Which driver to use (psycopg)
# - How to open and manage connections
#
# echo=True prints every SQL query in the terminal.
# It is useful while learning and debugging.
#
engine = create_engine(
    DATABASE_URL,
    echo=True
)


# -----------------------------------------------------
# Create Session Factory
# -----------------------------------------------------
# SessionLocal is NOT a database session.
#
# It is a factory that creates new database
# sessions whenever FastAPI receives a request.
#
# autocommit=False
#     Changes are NOT automatically saved.
#
# autoflush=False
#     SQLAlchemy will not automatically send
#     changes to the database until instructed.
#
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)


# -----------------------------------------------------
# Base Class
# -----------------------------------------------------
# Every database model will inherit from Base.
#
# Example:
#
# class Event(Base):
#     ...
#
class Base(DeclarativeBase):
    pass


# -----------------------------------------------------
# Dependency
# -----------------------------------------------------
# Creates a database session.
#
# FastAPI will use this function later
# inside API endpoints.
#
# A new session is created for every request.
#
# After the request finishes,
# the session is automatically closed.
#
def get_db():

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close()