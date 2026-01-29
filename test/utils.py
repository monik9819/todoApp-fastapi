from sqlalchemy import create_engine, StaticPool, text
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from ..routers.auth import bcrypt_context
from ..database import Base
from ..models import Todos, Users
from ..main import app
import pytest


SQLALCHEMY_DATABASE_URL = f"sqlite:///./testdb.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def override_get_current_user():
    return {'username': 'admin', 'id':1, 'user_role':'admin'}


client = TestClient(app)


@pytest.fixture
def test_todo():
    todo = Todos(title="learn FastAPI", description="learn then build and develop apps", priority="3", complete=False,
                 owner_id=1)
    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield todo # sends control back to test function test_read_all_authenticated is executed

    # this is executed post completion of test, it cleans db so every test starts with fresh db
    with engine.connect() as con:
        con.execute(text("DELETE FROM todos;"))
        con.commit()

@pytest.fixture
def test_user():
    user = Users(username='admin', firstname='monik', lastname='monik', email='admin@yahoo.com',
                 hashed_password=bcrypt_context.hash('monik@admin'), role='admin', is_active=True, phone_num='888-88-88888')
    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    yield user
    with engine.connect() as con:
        con.execute(text("DELETE FROM users;"))
        con.commit()