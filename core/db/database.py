from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker

import settings

SQLALCHEMY_DB_URL = f"postgresql+psycopg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_URL}/{settings.DB_NAME}"
engine = create_engine(SQLALCHEMY_DB_URL)
SessionLocal = sessionmaker(autoflush=False, bind=engine)

def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
