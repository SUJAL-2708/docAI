from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from backend.config import settings


# ==========================================
# POSTGRESQL DATABASE ENGINE
# ==========================================

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.DEBUG
)


# ==========================================
# DATABASE SESSION FACTORY
# ==========================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# ==========================================
# SQLALCHEMY BASE CLASS
# ==========================================

class Base(DeclarativeBase):
    pass


# ==========================================
# FASTAPI DATABASE DEPENDENCY
# ==========================================

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()