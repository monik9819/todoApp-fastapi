from ..models import Todos
from typing import Annotated
from starlette import status
from .auth import get_current_user
from sqlalchemy.orm import Session
from ..database import SessionLocal
from pydantic import BaseModel, Field
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from fastapi import APIRouter, Depends, HTTPException, Path, Request

templates = Jinja2Templates(directory="TodoApp/templates")

router = APIRouter(prefix='/todos', tags=["todos"])

class TodoRequest(BaseModel):
    title: str = Field(min_length=3, max_length=100)
    description: str = Field(max_length=300)
    priority: int = Field(gt=0, le=5)
    complete: bool

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

def redirect_to_login():
    redirect_response = RedirectResponse(url="/auth/login-page", status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie(key="access_token")
    return redirect_response

### pages ###
@router.get("/todo-page")
async def render_todo_page(request: Request, db: db_dependency):
    try:
        token = request.cookies.get('access_token')
        print(
            f"Token from cookie: {token}")  # Debug line
        if token is None:
            print("No token found in cookies")
            return redirect_to_login()
        user = await get_current_user(token)
        print(
            f"User: {user}")  # Debug line
        if user is None:
            return redirect_to_login()
        todos = db.query(Todos).filter(Todos.owner_id == user.get("id")).all()
        return templates.TemplateResponse("todo.html", {"request": request, "todos": todos, "user": user})

    except Exception as e:
        print(
            f"Exception occurred: {e}")  # See the actual error
        return redirect_to_login()

@router.get("/add-todo-page")
async def render_add_todo_page(request: Request, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get('access_token'))
        if user is None:
            return redirect_to_login()
        return templates.TemplateResponse("add-todo.html", {"request": request, "user": user})
    except Exception as e:
        print(
            f"Exception occurred: {e}")  # See the actual error
        return redirect_to_login()

@router.get("/edit-todo-page/{todo_id}")
async def render_edit_todo_page(request: Request, todo_id: int, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get('access_token'))
        if user is None:
            return redirect_to_login()
        todo = db.query(Todos).filter(Todos.id == todo_id).first()
        return templates.TemplateResponse("edit-todo.html", {"request": request, "todo": todo, "user": user})
    except Exception as e:
        print(
            f"Exception occurred: {e}")
        return redirect_to_login()



    ### endpoints ###
@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    todo_list = db.query(Todos).filter_by(owner_id=user.get('id')).all()
    if todo_list:
        return todo_list
    else:
        return ['No task added for user']

@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
def read_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(todo_id == Todos.id).filter(user.get('id') == Todos.owner_id).first()
    if todo_model:
        return todo_model
    raise HTTPException(status_code=404, detail="todo id doesn't exist")

@router.post("/todo/create", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, todo_req: TodoRequest, db: db_dependency):
    todo_model = Todos(**todo_req.model_dump(), owner_id=user.get('id'))
    db.add(todo_model)
    db.commit()
    return "task added"


@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency, db: db_dependency, todo_req: TodoRequest, todo_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(user.get('id') == Todos.owner_id).filter(todo_id == Todos.id).first()
    if not todo_model:
        raise HTTPException(status_code=404, detail="Todo id doesn't exist")

    todo_model.title = todo_req.title
    todo_model.description = todo_req.description
    todo_model.priority = todo_req.priority
    todo_model.complete = todo_req.complete

    db.add(todo_model)
    db.commit()

@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(user.get('id') == Todos.owner_id).filter_by(id=todo_id).first()
    if not todo_model:
        raise HTTPException(status_code=404, detail="Todo id doesn't exist, can't delete it")

    db.delete(todo_model)
    # db.query(Todos).filter(user.get('id') == Todos.owner_id).filter_by(id=todo_id).delete()
    db.commit()
