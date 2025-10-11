from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# Player Schemas
class PlayerStats(BaseModel):
    dribbling: int
    finishing: int
    passing: int
    defense: int
    speed: int
    strength: int

class RecentPerformance(BaseModel):
    goals: int
    assists: int
    average_rating: float
    minutes_played: int

class PlayerBase(BaseModel):
    name: str
    position: str
    team: str
    age: int
    nationality: str
    avatar: Optional[str] = None
    stats: PlayerStats
    recent_performance: RecentPerformance

class PlayerCreate(PlayerBase):
    id: str

class Player(PlayerBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Video Highlight Schemas
class Timestamp(BaseModel):
    start: int
    end: int

class AIInsights(BaseModel):
    confidence: int
    analysis: str
    key_moments: List[str]

class VideoHighlightBase(BaseModel):
    title: str
    thumbnail: str
    video_url: str
    duration: str
    match: str
    date: datetime
    type: str  # "strength", "weakness", "neutral"
    tags: List[str]
    player_id: str
    description: str
    timestamp: Timestamp
    ai_insights: AIInsights

class VideoHighlightCreate(VideoHighlightBase):
    id: str

class VideoHighlight(VideoHighlightBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Search Result Schema
class SearchResult(BaseModel):
    type: str  # "player", "highlight", "match"
    id: str
    title: str
    description: str
    relevance_score: float

# AI Analysis Schemas (for future AI integration)
class VideoAnalysisRequest(BaseModel):
    video_url: str
    analysis_type: Optional[str] = "comprehensive"

class VideoAnalysisResponse(BaseModel):
    video_url: str
    analysis_id: str
    status: str
    insights: Optional[Dict[str, Any]] = None
    confidence: Optional[float] = None

class PlayerReportRequest(BaseModel):
    player_id: str
    report_type: Optional[str] = "comprehensive"
    include_video_analysis: Optional[bool] = True

class PlayerReportResponse(BaseModel):
    player_id: str
    report_id: str
    status: str
    report: Optional[Dict[str, Any]] = None
    generated_at: Optional[datetime] = None
