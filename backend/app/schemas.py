from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.models import TransactionCategoryEnum

class TransactionBase(BaseModel):
    date: datetime
    description: str
    amount: float
    raw_text: Optional[str] = None
    category: TransactionCategoryEnum = TransactionCategoryEnum.UNCATEGORIZED

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdateCategory(BaseModel):
    category: TransactionCategoryEnum

class Transaction(TransactionBase):
    id: int
    owner_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class MonthlySummaryItem(BaseModel):
    category: TransactionCategoryEnum
    total_amount: float

class MonthlySummaryResponse(BaseModel):
    month: str
    summary: List[MonthlySummaryItem]

# Rule schemas
class RuleBase(BaseModel):
    name: str
    pattern: str
    category: TransactionCategoryEnum
    priority: int = 100
    is_active: bool = True

class RuleCreate(RuleBase):
    pass

class RuleUpdate(BaseModel):
    name: Optional[str] = None
    pattern: Optional[str] = None
    category: Optional[TransactionCategoryEnum] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None

class Rule(RuleBase):
    id: int
    owner_id: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True
