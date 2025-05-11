from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional
import pandas as pd
import io
from datetime import datetime

from app import crud, schemas, models
from app.database import get_db
from app.routers.auth import get_current_active_user

router = APIRouter()

@router.post("/upload-csv/", summary="Upload bank statement CSV")
async def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_current_active_user)
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a CSV.")
    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))

        required_columns = {'Date', 'Description', 'Amount'}
        if not required_columns.issubset(df.columns):
            raise HTTPException(status_code=400, detail=f"CSV must contain columns: {', '.join(required_columns)}")

        try:
            df['Date'] = pd.to_datetime(df['Date'])
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error parsing Date column: {str(e)}. Ensure dates are in a recognizable format.")

        user_id = current_user.id if current_user else None
        result = crud.bulk_create_transactions_from_df(db, df, user_id=user_id)
        return result
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="Uploaded CSV file is empty.")
    except Exception as e:
        print(f"Error processing CSV: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing CSV file: {str(e)}")

@router.get("/", response_model=List[schemas.Transaction])
def read_transactions(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_current_active_user)
):
    user_id = current_user.id if current_user else None
    transactions = crud.get_transactions(db, user_id=user_id, skip=skip, limit=limit)
    return transactions

# Rule endpoints
@router.get("/rules/", response_model=List[schemas.Rule])
def read_rules(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    rules = crud.get_rules(db, user_id=current_user.id, skip=skip, limit=limit)
    return rules

@router.post("/rules/", response_model=schemas.Rule)
def create_rule(
    rule: schemas.RuleCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    return crud.create_rule(db, rule, user_id=current_user.id)

@router.put("/rules/{rule_id}/", response_model=schemas.Rule)
def update_rule(
    rule_id: int,
    rule_update: schemas.RuleUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    updated_rule = crud.update_rule(db, rule_id, rule_update, user_id=current_user.id)
    if not updated_rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return updated_rule

@router.delete("/rules/{rule_id}/", response_model=bool)
def delete_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    success = crud.delete_rule(db, rule_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Rule not found")
    return True

@router.patch("/{transaction_id}/category", response_model=schemas.Transaction)
def update_transaction_category_api(
    transaction_id: int,
    category_update: schemas.TransactionUpdateCategory,
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_current_active_user)
):
    user_id = current_user.id if current_user else None
    db_transaction = crud.update_transaction_category(db, transaction_id=transaction_id, category_update=category_update, user_id=user_id)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return db_transaction

@router.get("/summary/monthly/{year}/{month}", response_model=schemas.MonthlySummaryResponse)
def get_monthly_summary(
    year: int = Path(..., title="Year", ge=2000, le=datetime.now().year + 5),
    month: int = Path(..., title="Month", ge=1, le=12),
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_current_active_user)
):
    user_id = current_user.id if current_user else None
    summary_items = crud.get_monthly_spending_summary(db, year=year, month=month, user_id=user_id)
    return schemas.MonthlySummaryResponse(month=f"{year}-{month:02d}", summary=summary_items)
