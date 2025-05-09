from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class TransactionCategoryEnum(str, enum.Enum):
    UNCATEGORIZED = "Uncategorized"
    FOOD_DRINK = "Food & Drink"
    TRANSPORT = "Transport"
    SHOPPING = "Shopping"
    HOUSING = "Housing"
    UTILITIES = "Utilities"
    ENTERTAINMENT = "Entertainment"
    HEALTHCARE = "Healthcare"
    EDUCATION = "Education"
    INCOME = "Income"
    OTHER = "Other"

class User(Base): # For Bonus: Authentication
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    transactions = relationship("Transaction", back_populates="owner")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime(timezone=True), nullable=False)
    description = Column(String, index=True)
    amount = Column(Float, nullable=False)
    raw_text = Column(String, nullable=True)
    category = Column(SAEnum(TransactionCategoryEnum), default=TransactionCategoryEnum.UNCATEGORIZED, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    owner = relationship("User", back_populates="transactions")
