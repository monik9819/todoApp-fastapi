from typing import Annotated
from starlette import status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from ..database import SessionLocal
from fastapi import APIRouter, Depends, HTTPException, Path
from .auth import get_current_user, bcrypt_context, authenticate_user
from ..models import Users

router = APIRouter(prefix="/user", tags=["user"])

class UpdateUser(BaseModel):
    password: str = Field(min_length=8)
    new_password: str = Field(min_length=8)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/", status_code=status.HTTP_200_OK)
async def get_users(db: db_dependency, user: user_dependency):
    user_data = db.query(Users).filter_by(id=user.get("id")).first()
    if not user_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user_data

@router.patch("/change_password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(db: db_dependency, user: user_dependency, user_password: UpdateUser):
    if user_password.new_password == user_password.password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="old and new password cannot be the same")
    user_data = db.query(Users).filter(user.get("id") == Users.id).first()
    if not user_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not authenticate_user(user_data.username, user_password.password, db):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")
    new_hashed_password = bcrypt_context.hash(user_password.new_password)
    user_data.hashed_password = new_hashed_password
    db.add(user_data)
    db.commit()

@router.put("/add/phone_number", status_code=status.HTTP_204_NO_CONTENT)
async def add_phone_number(db: db_dependency, user: user_dependency, phone_num: str):
    user_data = db.query(Users).filter(user.get("id") == Users.id).first()
    if not user_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user_data.phone_num = phone_num
    db.add(user_data)
    db.commit()
