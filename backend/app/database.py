import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

BASE = Path(__file__).resolve().parents[1]
db_url = os.getenv("DATABASE_URL", f"sqlite:///{BASE / 'data' / 'retail.db'}")
Path(BASE / "data").mkdir(parents=True, exist_ok=True)
connect_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {}
engine = create_engine(db_url, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
