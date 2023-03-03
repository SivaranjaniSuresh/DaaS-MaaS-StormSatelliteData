import datetime

from database import get_db_session
from sqlalchemy import Column, DateTime, Integer, String

SessionLocal, Base, engine = get_db_session()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    username = Column(String)
    password = Column(String)
    mobile = Column(String)
    credit_card = Column(String)
    service = Column(String)
    calls_remaining = Column(Integer)


class UserActivity(Base):
    __tablename__ = "user_activity"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    username = Column(String)
    request_type = Column(String)
    api_endpoint = Column(String)
    response_code = Column(String)
    description = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
