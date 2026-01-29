from .utils import *
from ..routers.users import get_db, get_current_user
from starlette import status


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_get_users(test_user):
    response = client.get('/user/')

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['username'] == test_user.username
    assert response.json()['id'] == test_user.id
    assert response.json()['email'] == test_user.email
    assert response.json()['firstname'] == test_user.firstname
    assert response.json()['lastname'] == test_user.lastname
    assert response.json()['is_active'] == test_user.is_active
    assert response.json()['phone_num'] == test_user.phone_num

def test_change_password(test_user):
    user_password = {'password': 'monik@admin', 'new_password': 'ADMIN@monik'}
    response = client.patch('/user/change_password', json=user_password)
    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_change_password_NEG(test_user):
    user_password = {'password': 'monikmonik', 'new_password': '112345678'}
    response = client.patch('/user/change_password', json=user_password)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Incorrect password"}

    user_password = {'password': 'monik@admin', 'new_password': 'monik@admin'}
    response = client.patch('/user/change_password', json=user_password)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "old and new password cannot be the same"}

    app.dependency_overrides[get_current_user] = lambda: {'username': 'admin', 'id':2, 'user_role':'admin'}
    user_password = {'password': 'monik@admin', 'new_password': 'ADMIN@monik'}
    response = client.patch('/user/change_password', json=user_password)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "User not found"}

    app.dependency_overrides[get_current_user] = override_get_current_user

def test_add_phone_number(test_user):
    response = client.put('/user/add/phone_number?phone_num=987654321')
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    user_data = db.query(Users).filter(1 == Users.id).first()
    assert user_data.phone_num == '987654321'
    assert user_data.username == 'admin'
