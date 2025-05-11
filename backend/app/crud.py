from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from . import models, schemas
from typing import List, Optional, Dict
from datetime import datetime
import pandas as pd
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Rule management functions
def get_rules(db: Session, user_id: Optional[int] = None, skip: int = 0, limit: int = 100):
    query = db.query(models.Rule)
    if user_id:
        query = query.filter(models.Rule.owner_id == user_id)
    return query.offset(skip).limit(limit).all()

def create_rule(db: Session, rule: schemas.RuleCreate, user_id: Optional[int] = None):
    db_rule = models.Rule(
        name=rule.name,
        pattern=rule.pattern,
        category=rule.category,
        priority=rule.priority,
        owner_id=user_id
    )
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule

def update_rule(db: Session, rule_id: int, rule_update: schemas.RuleUpdate, user_id: Optional[int] = None):
    db_rule = db.query(models.Rule).filter(models.Rule.id == rule_id)
    if user_id:
        db_rule = db_rule.filter(models.Rule.owner_id == user_id)
    
    db_rule = db_rule.first()
    if not db_rule:
        return None
    
    for key, value in rule_update.dict(exclude_unset=True).items():
        setattr(db_rule, key, value)
    
    db.commit()
    db.refresh(db_rule)
    return db_rule

def delete_rule(db: Session, rule_id: int, user_id: Optional[int] = None):
    db_rule = db.query(models.Rule).filter(models.Rule.id == rule_id)
    if user_id:
        db_rule = db_rule.filter(models.Rule.owner_id == user_id)
    
    db_rule = db_rule.first()
    if not db_rule:
        return False
    
    db.delete(db_rule)
    db.commit()
    return True

def get_active_rules(db: Session, user_id: Optional[int] = None) -> List[models.Rule]:
    """Get all active rules for a user, sorted by priority."""
    query = db.query(models.Rule).filter(models.Rule.is_active == True)
    if user_id:
        query = query.filter(models.Rule.owner_id == user_id)
    return query.order_by(models.Rule.priority).all()

def create_transaction(db: Session, transaction: schemas.TransactionCreate, user_id: Optional[int] = None):
    """Create a new transaction and automatically categorize it using rules."""
    db_transaction = models.Transaction(
        date=transaction.date,
        description=transaction.description,
        amount=transaction.amount,
        raw_text=transaction.raw_text,
        category=transaction.category,
        owner_id=user_id
    )
    
    # Get active rules for this user
    rules = get_active_rules(db, user_id)
    
    # If no category specified or it's UNCATEGORIZED, try to auto-categorize
    if transaction.category == models.TransactionCategoryEnum.UNCATEGORIZED:
        db_transaction.categorize(rules)
    
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def create_transaction(db: Session, transaction: schemas.TransactionCreate, user_id: Optional[int] = None):
    if transaction.category == models.TransactionCategoryEnum.UNCATEGORIZED:
        transaction.category = auto_categorize_transaction(transaction.description, transaction.raw_text, transaction.amount)

    db_transaction = models.Transaction(
        **transaction.model_dump(),
        owner_id=user_id
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def get_transactions(db: Session, user_id: Optional[int] = None, skip: int = 0, limit: int = 100):
    query = db.query(models.Transaction)
    if user_id:
        query = query.filter(models.Transaction.owner_id == user_id)
    return query.order_by(models.Transaction.date.desc()).offset(skip).limit(limit).all()

def get_transaction(db: Session, transaction_id: int, user_id: Optional[int] = None):
    query = db.query(models.Transaction).filter(models.Transaction.id == transaction_id)
    if user_id:
        query = query.filter(models.Transaction.owner_id == user_id)
    return query.first()

def update_transaction_category(db: Session, transaction_id: int, category_update: schemas.TransactionUpdateCategory, user_id: Optional[int] = None):
    db_transaction = get_transaction(db, transaction_id, user_id)
    if db_transaction:
        db_transaction.category = category_update.category
        db.commit()
        db.refresh(db_transaction)
    return db_transaction

def bulk_create_transactions_from_df(db: Session, df: pd.DataFrame, user_id: Optional[int] = None):
    transactions_to_create = []
    for _, row in df.iterrows():
        category = auto_categorize_transaction(row['Description'], row.get('RawText'), row['Amount'])
        transaction_data = schemas.TransactionCreate(
            date=pd.to_datetime(row['Date']),
            description=row['Description'],
            amount=row['Amount'],
            raw_text=row.get('RawText'),
            category=category
        )
        db_transaction = models.Transaction(**transaction_data.model_dump(), owner_id=user_id)
        transactions_to_create.append(db_transaction)

    db.add_all(transactions_to_create)
    db.commit()
    return {"message": f"{len(transactions_to_create)} transactions created successfully."}

def get_monthly_spending_summary(db: Session, year: int, month: int, user_id: Optional[int] = None) -> List[schemas.MonthlySummaryItem]:
    query = db.query(
        models.Transaction.category,
        func.sum(models.Transaction.amount).label("total_amount")
    ).filter(
        extract('year', models.Transaction.date) == year,
        extract('month', models.Transaction.date) == month,
        models.Transaction.amount < 0
    )
    if user_id:
        query = query.filter(models.Transaction.owner_id == user_id)

    summary_data = query.group_by(models.Transaction.category).all()
    return [schemas.MonthlySummaryItem(category=cat, total_amount=total) for cat, total in summary_data]
