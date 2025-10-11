from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Database URL - using SQLite for development, PostgreSQL for production
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./scoutpulse.db")

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

# Player Model
class PlayerModel(Base):
    __tablename__ = "players"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    position = Column(String)
    team = Column(String, index=True)
    age = Column(Integer)
    nationality = Column(String)
    avatar = Column(String, nullable=True)
    
    # Stats as JSON field
    stats = Column(JSON)
    
    # Recent performance as JSON field
    recent_performance = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Video Highlight Model
class VideoHighlightModel(Base):
    __tablename__ = "video_highlights"
    
    id = Column(String, primary_key=True, index=True)
    title = Column(String, index=True)
    thumbnail = Column(String)
    video_url = Column(String)
    duration = Column(String)
    match = Column(String, index=True)
    date = Column(DateTime, index=True)
    type = Column(String, index=True)  # "strength", "weakness", "neutral"
    tags = Column(JSON)  # List of tags
    player_id = Column(String, index=True)
    description = Column(Text)
    
    # Timestamp as JSON field
    timestamp = Column(JSON)
    
    # AI insights as JSON field
    ai_insights = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
