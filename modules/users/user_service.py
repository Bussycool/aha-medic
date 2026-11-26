from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pwdlib import PasswordHash

# Import your existing database session generator, SQLAlchemy model, and Pydantic schemas
from database import get_db
from models import User
from schemas import UserCreate, UserResponse

app = FastAPI()
password_hash = PasswordHash.recommended()

@app.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # 1. Check if the email already exists in the database
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # 2. Hash the plain-text password
    hashed_pw = password_hash.hash(user.password)
    
    # 3. Create the database model instance
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_pw
    )
    
    # 4. Save to the database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # Fetches the auto-generated ID from the database
    
    return new_user
