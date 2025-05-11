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

class Rule(Base):
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    pattern = Column(String, nullable=False)  # Can be regex pattern
    category = Column(SAEnum(TransactionCategoryEnum), nullable=False)
    priority = Column(Integer, default=100)  # Lower number means higher priority
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    owner = relationship("User", back_populates="rules")

    def matches(self, text: str) -> bool:
        """Check if this rule matches the given text."""
        import re
        try:
            return bool(re.search(self.pattern, text, re.IGNORECASE))
        except re.error:
            return False

    def __repr__(self):
        return f"Rule(id={self.id}, pattern='{self.pattern}', category='{self.category}')"

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
    notes = Column(String, nullable=True)  # For manual notes about the transaction

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    owner = relationship("User", back_populates="transactions")

    def categorize(self, rules: list[Rule]) -> None:
        """Automatically categorize this transaction based on rules."""
        if not rules:
            return

        # Sort rules by priority (lower number = higher priority)
        rules = sorted(rules, key=lambda r: r.priority)

        # Try each rule in order of priority
        for rule in rules:
            if rule.is_active and (rule.matches(self.description) or (self.raw_text and rule.matches(self.raw_text))):
                self.category = rule.category
                self.updated_at = func.now()
                return

    def __repr__(self):
        return f"Transaction(id={self.id}, description='{self.description}', amount={self.amount}, category='{self.category}')"
