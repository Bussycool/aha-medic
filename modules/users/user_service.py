from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..users.enums.role_enum import Role
from database_config import get_db
from .models.user_model import User




async def create_user(email: str, name: str, password: str, role: Role, db: Session = Depends(get_db)):
  try:
    existing_user = db.query(User).filter(User.email == email).first()
    if(existing_user):
      raise HTTPException(detail="User with this email already exists, please login.", status_code=status.HTTP_400_BAD_REQUEST)

    new_user = User(
      email=email,
      name=name,
      password=password,
      role=role
    )
    db.add(new_user)
    db.commit()
    return new_user
  except HTTPException as e:
    raise e

