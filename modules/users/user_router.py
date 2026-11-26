from fastapi import APIRouter, Depends
from modules.users import user_service
from database_config import get_db
from sqlalchemy.orm import Session
from modules.users.dtos.create_user_dto import CreateUserDto


router = APIRouter(tags=["Users"], prefix="/users")


@router.post("/register")
async def create_user(body: CreateUserDto, db:Session=Depends(get_db)):
  return await user_service.create_user(
    body.email,
    body.name,
    body.password,
    body.role,
    db
  )