from .utils import *
from ..routers.auth import get_db, get_current_user, authenticate_user, create_access_token, SECRET_KEY, ALGORITHM
from fastapi import HTTPException
from datetime import timedelta
from starlette import status
from jose import jwt
import pytest


app.dependency_overrides[get_db] = override_get_db


def test_authenticate_user(test_user):
    db = TestingSessionLocal()

    auth_user = authenticate_user(test_user.username, "monik@admin", db)
    assert auth_user is not None
    assert auth_user.id == test_user.id
    assert auth_user.username == test_user.username

    nan_auth_user_1 = authenticate_user(test_user.username, "admin@admin", db)
    assert nan_auth_user_1 is False

    nan_auth_user_2 = authenticate_user("wrong_username", "admin@admin", db)
    assert nan_auth_user_2 is False

def test_create_access_token():
    username = 'testuser'
    user_id = 1
    role = 'user'
    expires_delta = timedelta(days=1)

    token = create_access_token(username, user_id, role, expires_delta)
    # why added  options={'verify_signature': False}
    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={'verify_signature': False})

    assert decoded_token['sub'] == username
    assert decoded_token['id'] == user_id
    assert decoded_token['role'] == role

@pytest.mark.asyncio
async def test_get_current_user():
    encode = {'sub': 'testuser', 'id': 1, 'role': 'admin'}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    user = await get_current_user(token=token)
    assert user == {'username': 'testuser', 'id': 1, 'user_role': 'admin'}

@pytest.mark.asyncio
async def test_get_current_user_NEG():
    encode = {'role': 'user'}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(token=token)

    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == 'Could not validate credentials'


def test_create_user(test_user):
    request_data = {"email": "admin@gmail.com", "password": "monik@admin", "username": "monik", "firstname": "monik",
                    "lastname": "monik", "role": "admin", "phone_num": "888-88-88888"}
    response = client.post('/auth/', json=request_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"message": "User created", "user": "monik"}

def test_create_user_NEG():
    request_data = {"email": "admin@yahoo.com", "password": "monik", "username": "admin", "firstname": "monik",
                    "lastname": "monik", "role": "admin", "phone_num": "888-88-88888"}
    response = client.post('/auth/', json=request_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

def test_login_for_access_token(test_user):
    response = client.post('auth/token', data={'username': 'admin', 'password': 'monik@admin'})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['token_type'] == 'bearer'

    decoded_token = jwt.decode(response.json()["access_token"], SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded_token["sub"] == test_user.username
    assert decoded_token["id"] == test_user.id
    assert decoded_token["role"] == test_user.role

def test_login_for_access_token_NEG():
    response = client.post('auth/token', data={'username': 'monik', 'password': 'monik@admin'})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
