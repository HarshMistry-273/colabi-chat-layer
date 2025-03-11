from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()

engine = create_engine(
    os.getenv('DATABASE_URL'),
    pool_size=10,
    max_overflow=20,
    pool_timeout=300,
    pool_recycle=1800
    )

print("DATABASE URL: ", os.getenv('DATABASE_URL'))

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()

def get_db_session():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()