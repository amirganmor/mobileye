# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from users import router as users_router  # Importing users router
from books import router as books_router  # Importing books router
from database import engine, Base
from config import ADMIN_USERNAME, ADMIN_PASSWORD, USER_USERNAME, USER_PASSWORD

# Create all database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()
security = HTTPBasic()

# Sample user data (for demonstration)
fake_users_db = {
    ADMIN_USERNAME: ADMIN_PASSWORD,
    USER_USERNAME: USER_PASSWORD
}



# Dependency to authenticate users
def authenticate_user(credentials: HTTPBasicCredentials = Depends(security)):
    user = fake_users_db.get(credentials.username)
    if user is None or user != credentials.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# Example protected endpoint
@app.get("/protected")
def protected_route(username: str = Depends(authenticate_user)):
    return {"message": f"Hello, {username}. This is a protected route!"}

# Include routers
app.include_router(users_router, prefix="/users", tags=["users"])  # Adding prefix for organization
app.include_router(books_router, prefix="/books", tags=["books"])  # Adding prefix for organization

@app.get("/")
def read_root():
    return {"message": "Welcome to the Mobileye Library Management System!"}
