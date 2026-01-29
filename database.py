import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

# to connect to sqlite db, below is connection for mysql
# SQLALCHEMY_DATABASE_URL = "sqlite:///testdb.db"
# engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# need PyMySQL lib for driver to connect mysql db
# SQLALCHEMY_DATABASE_URL = 'mysql+pymysql://root:root@127.0.0.1:3306/TodoApplicationDatabase'
# engine = create_engine(SQLALCHEMY_DATABASE_URL)

# need psycopg2-binary ib for driver to connect postgresql db
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
if not SQLALCHEMY_DATABASE_URL:
    print(SQLALCHEMY_DATABASE_URL)
    print(os.getenv("DATABASE_URL"))

    raise ValueError("Environment variables aren't set")

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
