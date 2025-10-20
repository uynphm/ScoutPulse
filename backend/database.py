from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DB_PATH = BASE_DIR / "scoutpulse.db"

def resolve_database_url() -> str:
    env_url = os.getenv("DATABASE_URL")

    if not env_url:
        return f"sqlite:///{DEFAULT_DB_PATH}"

    if env_url.startswith("sqlite:///"):
        raw_path = env_url.replace("sqlite:///", "", 1)
        raw_path_path = Path(raw_path)

        if not raw_path_path.is_absolute():
            resolved_path = (BASE_DIR / raw_path_path).resolve()
            return f"sqlite:///{resolved_path}"

        return env_url

    return env_url

# Database URL - using SQLite for development, PostgreSQL for production
DATABASE_URL = resolve_database_url()

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
