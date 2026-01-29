from fastapi import FastAPI, Request
from .models import Base
from .database import engine
from starlette import status
from fastapi.staticfiles import StaticFiles
from .routers import auth, todos, admin, users
from fastapi.responses import RedirectResponse

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="TodoApp/static"), name="static")


@app.get("/")
def test(request: Request):
    # throws internal error without request
    return RedirectResponse(url="/todos/todo-page", status_code=status.HTTP_302_FOUND)

@app.get("/health_check")
def health_check():
    return {"status": "ok"}


app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(users.router)
app.include_router(todos.router)
