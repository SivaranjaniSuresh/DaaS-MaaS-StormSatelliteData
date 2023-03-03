from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


def get_db_session():
    SQLALCHEMY_DATABASE_URL = "sqlite:////fastapi/users.db"
    # SQLALCHEMY_DATABASE_URL = "sqlite:///./users.db"
    # Create a database engine and sessionmaker
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    # Define a base class for your ORM classes
    Base = declarative_base()

    # Return a tuple of the sessionmaker and base objects
    return SessionLocal, Base, engine
