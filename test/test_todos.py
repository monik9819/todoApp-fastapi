from .utils import *
from ..routers.todos import get_db, get_current_user
from starlette import status


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_read_all(test_todo):
    response = client.get("/todos")
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

def test_read_todo(test_todo):
    response = client.get("/todos/todo/1")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "learn FastAPI"
    assert data["description"] == "learn then build and develop apps"
    assert data["priority"] == 3
    assert data["complete"] == False
    assert data["owner_id"] == 1
    assert data["id"] == 1
    assert "created_at" in data
    assert "updated_at" in data

def test_read_todo_NEG(test_todo):
    response = client.get("/todos/todo/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': "todo id doesn't exist"}

def test_create_todo(test_todo):
    request_data = {"title": "example todo", "description": "lorem ispum lorem ispum lorem ispum", "priority": 3,
                    "complete": False}
    response = client.post('/todos/todo/create', json=request_data)
    assert response.status_code == status.HTTP_201_CREATED

    db = TestingSessionLocal()
    model = db.query(Todos).filter(2==Todos.id).first()
    assert model.title == request_data["title"]
    assert model.description == request_data["description"]
    assert model.priority == request_data["priority"]
    assert model.complete == request_data["complete"]
    assert model.id == 2
    assert model.owner_id == 1

def test_create_todo_NEG(test_todo):
    request_data = {"description": "lorem ispum lorem ispum lorem ispum", "priority": 3, "complete": False}
    response = client.post('/todos/todo/create', json=request_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    request_data = {"title": "example todo", "description": "lorem ispum lorem ispum lorem ispum", "priority": 3}
    response = client.post('/todos/todo/create', json=request_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    request_data = {"title": "example todo", "description": "lorem ispum lorem ispum lorem ispum", "priority": 0,
                    "complete": False}
    response = client.post('/todos/todo/create', json=request_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    request_data = {"title": "ex", "description": "lorem ispum lorem ispum lorem ispum", "priority": 5,
                    "complete": False}
    response = client.post('/todos/todo/create', json=request_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

def test_update_todo(test_todo):
    request_data = {"title": "example change tile", "description": "change des lorem ispum lorem ispum lorem ispum", "priority": 1,
                    "complete": True}
    response = client.put("/todos/todo/1", json=request_data)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    model = db.query(Todos).filter(1 == Todos.id).first()
    assert model.title == request_data["title"]
    assert model.description == request_data["description"]
    assert model.priority == request_data["priority"]
    assert model.complete == request_data["complete"]
    assert model.id == 1
    assert model.owner_id == 1

def test_update_todo_NEG(test_todo):
    request_data = {"title": "example change tile", "description": "change des lorem ispum lorem ispum lorem ispum", "priority": 1,
                    "complete": True}
    response = client.put("/todos/todo/999", json=request_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_delete_todo(test_todo):
    response = client.delete("/todos/todo/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    model = db.query(Todos).filter(1==Todos.id).first()
    assert model is None

def test_delete_todo_NEG(test_todo):
    response = client.delete("/todos/todo/2")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail":"Todo id doesn't exist, can't delete it"}
