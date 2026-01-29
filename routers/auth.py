import os
from ..models import Users
from typing import Annotated
from starlette import status
from jose import jwt, JWTError
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from ..database import SessionLocal
from passlib.context import CryptContext
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, EmailStr
from datetime import timedelta, datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer


load_dotenv()

router = APIRouter(prefix="/auth", tags=["auth"])
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

if not SECRET_KEY or not ALGORITHM:
    raise ValueError("Environment variables aren't set")


class CreateUserRequest(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=100)
    firstname: str = Field(min_length=1)
    lastname: str
    password: str = Field(min_length=8)
    role: str
    phone_num: str

class Token(BaseModel):
    access_token: str
    token_type: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
templates = Jinja2Templates(directory="TodoApp/templates")

# pages #
@router.get("/login-page")
def render_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/register-page")
def render_register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


# end points #
def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user or (not bcrypt_context.verify(password, user.hashed_password)):
        return False
    return user

def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    expires = datetime.now(timezone.utc) + expires_delta
    to_encode = {'sub': username, 'id': user_id, 'role': role, 'exp': expires}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_role: str = payload.get('role')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
        return {'username': username, 'id': user_id, 'user_role': user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, user_req: CreateUserRequest):
    new_user = Users(email=user_req.email, username=user_req.username,
                     firstname=user_req.firstname, lastname=user_req.lastname,
                     hashed_password=bcrypt_context.hash(user_req.password),
                     role=user_req.role, is_active=True, phone_num=user_req.phone_num)

    db.add(new_user)
    db.commit()
    return {"message": "User created", "user": new_user.username}

@router.post("/token", response_model=Token, status_code=status.HTTP_200_OK)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=20))
    return {"access_token": token, "token_type": "bearer"}
