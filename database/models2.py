
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import uuid

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100))
    created_at = Column(DateTime, default=datetime.now())

    # Relationship with ChatMessage
    messages = relationship("ChatMessage", back_populates="user", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = 'chat_history'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    message = Column(Text, nullable=False)
    sent_at = Column(DateTime, default=datetime.now())

    # Relationship back to User
    user = relationship("User", back_populates="messages")


# Database setup
engine = create_engine('sqlite:///chat_app.db', echo=False)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)