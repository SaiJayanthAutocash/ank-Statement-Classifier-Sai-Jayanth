import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base
from app.core.config import settings

# Create a test database URL
SQLALCHEMY_DATABASE_URL_TEST = "sqlite:///./test.db"

# Create a new database engine for testing
engine = create_engine(
    SQLALCHEMY_DATABASE_URL_TEST, connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables for testing
Base.metadata.create_all(bind=engine)

# Dependency override for testing
@pytest.fixture
def db():
    """Yield a test database session"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Test client fixture
@pytest.fixture
def client():
    """Yield a test client"""
    return TestClient(app)

# Create a test user fixture
@pytest.fixture
def test_user(db):
    from app import crud, schemas
    
    user_data = schemas.UserCreate(
        username="testuser",
        password="testpassword"
    )
    return crud.create_user(db, user_data)

# Create a test token fixture
@pytest.fixture
def test_token(db, test_user):
    from app import crud
    
    token = crud.create_access_token(
        data={"sub": test_user.username},
        expires_delta=timedelta(minutes=30)
    )
    return token
