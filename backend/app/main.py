from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import engine, Base, get_db
from app.routers import transactions, auth
from app.core.config import settings
from app.models import User
from app.crud import create_user, get_user_by_username
from app.schemas import UserCreate
from sqlalchemy.orm import Session

# Create database tables
def create_db_and_tables():
    Base.metadata.create_all(bind=engine)
    # You can add a default user here for testing if you want
    # with Session(engine) as session:
    #     default_user = get_user_by_username(session, "testuser")
    #     if not default_user:
    #         user_in = UserCreate(username="testuser", password="testpassword")
    #         create_user(session, user_in)
    #         print("Default user 'testuser' created with password 'testpassword'")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up...")
    create_db_and_tables()
    print("Database tables created (if they didn't exist).")
    yield
    # Shutdown
    print("Shutting down...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# CORS settings
origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])
app.include_router(transactions.router, prefix=f"{settings.API_V1_STR}/transactions", tags=["Transactions"])

@app.get(settings.API_V1_STR, tags=["Root"])
async def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME} API"}
