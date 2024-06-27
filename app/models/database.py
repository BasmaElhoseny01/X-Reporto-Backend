# we use sqlalchemy to connect to the database
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
from elasticsearch import Elasticsearch
from app.core.config import configs

# Connect to Elasticsearch
es = Elasticsearch([configs.ELASTICSEARCH_URL])

# we use the database url from the environment variable DATABASE_URL
# SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
# SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://postgres:123456@localhost/dbname"
# create the sqlalchemy engine
engine = create_engine(configs.SQLALCHEMY_DATABASE_URL)

# create a sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# create the base class
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_database_if_not_exists():
    engine = create_engine(configs.SQLALCHEMY_DATABASE_URL)
    if not database_exists(engine.url):
        create_database(engine.url)
        print(f"Database created at {configs.SQLALCHEMY_DATABASE_URL}")
    else:
        print("Database already exists")

    # Create tables
    Base.metadata.create_all(bind=engine)