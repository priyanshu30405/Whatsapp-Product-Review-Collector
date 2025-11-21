"""SQLAlchemy models."""

from datetime import datetime
from enum import Enum

from sqlalchemy import Column, DateTime, Enum as PgEnum, Integer, String, Text

from .database import Base


class ConversationStep(str, Enum):
    PRODUCT = "product"
    USER = "user"
    REVIEW = "review"


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    contact_number = Column(String(30), nullable=False)
    user_name = Column(String(120), nullable=False)
    product_name = Column(String(120), nullable=False)
    product_review = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class ConversationState(Base):
    __tablename__ = "conversation_states"

    id = Column(Integer, primary_key=True, index=True)
    contact_number = Column(String(30), unique=True, nullable=False)
    step = Column(PgEnum(ConversationStep), nullable=False, default=ConversationStep.PRODUCT)
    product_name = Column(String(120), nullable=True)
    user_name = Column(String(120), nullable=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


