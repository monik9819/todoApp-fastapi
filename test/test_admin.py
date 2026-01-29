from .utils import *
from ..routers.admin import get_db, get_current_user
from starlette import status


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_get_todo(test_todo):
    response = client.get('/admin/todo')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "learn FastAPI"
    assert data[0]["description"] == "learn then build and develop apps"
    assert data[0]["priority"] == 3
    assert data[0]["complete"] == False
    assert data[0]["owner_id"] == 1
    assert data[0]["id"] == 1
    assert "created_at" in data[0]
    assert "updated_at" in data[0]

def test_get_todo_NEG():
    app.dependency_overrides[get_current_user] = lambda: {'username': 'admin', 'id':3, 'user_role':'nan'}
    response = client.get('/admin/todo')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Authentication failed"}

    app.dependency_overrides[get_current_user] = override_get_current_user

def test_delete_todo(test_todo):
    response = client.delete('/admin/todo/1')
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    model = db.query(Todos).filter(1 == Todos.id).first()
    assert model is None

def test_delete_todo_NEG(test_todo):
    response = client.delete('/admin/todo/2')

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo not found"}