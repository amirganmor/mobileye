from fastapi import FastAPI, HTTPException, Depends
from fastapi.testclient import TestClient
from pydantic import BaseModel
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from typing import Optional

# Define your Pydantic models
class UserCreate(BaseModel):
    username: str
    email: Optional[str] = None
    password: str

class UserOut(BaseModel):
    username: str
    email: Optional[str] = None

# Create the FastAPI app
app = FastAPI()

# Mock database session dependency
def get_db():
    db = MagicMock()  # Mocking the database session
    yield db

@app.post("/register", response_model=UserOut)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Example logic to create a user
    if user.username == "existing_user":
        raise HTTPException(status_code=400, detail="Username already registered")
    return UserOut(username=user.username, email=user.email)

# Create a test client for the FastAPI app
client = TestClient(app)

# Test cases
def test_create_user():
    # Define the user data
    user_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword"
    }

    # Send a POST request to create a new user
    response = client.post("/register", json=user_data)
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

def test_create_user_existing_username():
    # Define user data with an existing username
    user_data = {
        "username": "existing_user",
        "email": "existing_user@example.com",
        "password": "testpassword"
    }

    # Send a POST request to create a new user
    response = client.post("/register", json=user_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already registered"

# Run the tests if this file is run directly
if __name__ == "__main__":
    import pytest
    pytest.main([__file__])
