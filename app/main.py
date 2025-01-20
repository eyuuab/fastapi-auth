from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List

from app.database import SessionLocal
from app.models import User
from app.schemas import (
    UserCreate, 
    UserLogin, 
    UserResponse, 
    UserUpdate, 
    PasswordChange,
    TokenResponse
)
from app.auth import (
    get_password_hash, 
    verify_password, 
    create_access_token, 
    decode_token
)
import logging
import secrets

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="User Authentication API",
    description="A robust user authentication system with FastAPI",
    version="0.1.0"
)

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency to get current user from token
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Decode token
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    
    # Get email from token
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
    
    # Find user in database
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    
    return user

# Root endpoint
@app.get("/", tags=["Root"])
def root():
    return {"message": "Welcome to User Authentication API"}

# User Registration
@app.post("/register", response_model=dict, tags=["Authentication"])
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        logger.warning(f"Registration attempt with existing email: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Email already registered"
        )

    # Hash the password
    hashed_password = get_password_hash(user.password)
    new_user = User(
        email=user.email, 
        username=user.username, 
        hashed_password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    logger.info(f"User registered successfully: {user.email}")
    return {"message": "User registered successfully"}

# User Login
@app.post("/login", response_model=TokenResponse, tags=["Authentication"])
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    # Find user by email
    db_user = db.query(User).filter(User.email == user.email).first()
    
    # Validate credentials
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        logger.warning(f"Failed login attempt for email: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid credentials"
        )

    # Create access token
    access_token = create_access_token(data={"sub": db_user.email})
    
    logger.info(f"Successful login for email: {user.email}")
    return {"access_token": access_token, "token_type": "bearer"}

# Get Current User Profile
@app.get("/profile", response_model=UserResponse, tags=["User Management"])
def get_user_profile(current_user: User = Depends(get_current_user)):
    return current_user

# Update User Profile
@app.put("/profile", response_model=UserResponse, tags=["User Management"])
def update_user_profile(
    user_update: UserUpdate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    # Update username if provided
    if user_update.username is not None:
        current_user.username = user_update.username
    
    # Update email if provided and not already in use
    if user_update.email is not None:
        existing_user = db.query(User).filter(User.email == user_update.email).first()
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Email already in use"
            )
        current_user.email = user_update.email
    
    db.commit()
    db.refresh(current_user)
    
    return current_user

# Change Password
@app.post("/change-password", tags=["User Management"])
def change_password(
    password_change: PasswordChange, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    # Verify current password
    if not verify_password(password_change.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Current password is incorrect"
        )
    
    # Hash and update new password
    current_user.hashed_password = get_password_hash(password_change.new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}

# Protected Route (Example)
@app.get("/protected", tags=["Authentication"])
def protected_route(current_user: User = Depends(get_current_user)):
    """
    A protected route that requires a valid JWT token.
    Only authenticated users can access this route.
    """
    return {
        "message": "This is a protected route", 
        "user": {
            "email": current_user.email,
            "username": current_user.username
        }
    }

# List All Users (Admin-only route - for demonstration)
@app.get("/users", response_model=List[UserResponse], tags=["Admin"])
def list_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users
