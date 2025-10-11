from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional
import os
from dotenv import load_dotenv

from database import get_db, engine
from models import Base
from schemas import Player, VideoHighlight, SearchResult, PlayerCreate, VideoHighlightCreate
from crud import (
    get_player_by_id, get_all_players, create_player,
    get_highlights_by_player_id, get_highlight_by_id, create_highlight,
    search_players, search_highlights
)

# Load environment variables
load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="ScoutPulse API",
    description="AI-Powered Soccer Scouting Platform Backend",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for video serving
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return {"message": "ScoutPulse API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Player endpoints
@app.get("/api/players", response_model=List[Player])
async def get_players(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all players with pagination"""
    players = get_all_players(db, skip=skip, limit=limit)
    return players

@app.get("/api/players/{player_id}", response_model=Player)
async def get_player(player_id: str, db: Session = Depends(get_db)):
    """Get a specific player by ID"""
    player = get_player_by_id(db, player_id=player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player

@app.post("/api/players", response_model=Player)
async def create_new_player(player: PlayerCreate, db: Session = Depends(get_db)):
    """Create a new player"""
    return create_player(db=db, player=player)

# Video highlight endpoints
@app.get("/api/highlights", response_model=List[VideoHighlight])
async def get_highlights(
    player_id: Optional[str] = Query(None),
    highlight_type: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get video highlights with optional filtering"""
    if player_id:
        highlights = get_highlights_by_player_id(db, player_id=player_id)
    else:
        # Get all highlights (you might want to implement this in crud.py)
        highlights = []
    
    # Apply type filter if provided
    if highlight_type and highlight_type != "all":
        highlights = [h for h in highlights if h.type == highlight_type]
    
    return highlights[skip:skip + limit]

@app.get("/api/highlights/{highlight_id}", response_model=VideoHighlight)
async def get_highlight(highlight_id: str, db: Session = Depends(get_db)):
    """Get a specific video highlight by ID"""
    highlight = get_highlight_by_id(db, highlight_id=highlight_id)
    if not highlight:
        raise HTTPException(status_code=404, detail="Highlight not found")
    return highlight

@app.post("/api/highlights", response_model=VideoHighlight)
async def create_new_highlight(highlight: VideoHighlightCreate, db: Session = Depends(get_db)):
    """Create a new video highlight"""
    return create_highlight(db=db, highlight=highlight)

# Search endpoints
@app.get("/api/search", response_model=List[SearchResult])
async def search(
    q: str = Query(..., min_length=1),
    search_type: Optional[str] = Query("all", regex="^(all|players|highlights)$"),
    db: Session = Depends(get_db)
):
    """Search for players and highlights"""
    results = []
    
    if search_type in ["all", "players"]:
        players = search_players(db, query=q)
        results.extend([
            SearchResult(
                type="player",
                id=player.id,
                title=player.name,
                description=f"{player.position} • {player.team}",
                relevanceScore=0.9  # You can implement proper scoring
            )
            for player in players
        ])
    
    if search_type in ["all", "highlights"]:
        highlights = search_highlights(db, query=q)
        results.extend([
            SearchResult(
                type="highlight",
                id=highlight.id,
                title=highlight.title,
                description=highlight.description,
                relevanceScore=0.8  # You can implement proper scoring
            )
            for highlight in highlights
        ])
    
    return results

# AI Analysis endpoints (placeholder for future AI integration)
@app.post("/api/analyze-video")
async def analyze_video(video_url: str):
    """Analyze video for AI insights (placeholder)"""
    # This will integrate with Twelve Labs or IBM watsonx
    return {
        "message": "Video analysis endpoint - AI integration coming soon",
        "video_url": video_url,
        "status": "pending"
    }

@app.post("/api/generate-report/{player_id}")
async def generate_player_report(player_id: str, db: Session = Depends(get_db)):
    """Generate AI-powered player report (placeholder)"""
    player = get_player_by_id(db, player_id=player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    # This will integrate with IBM watsonx NLP
    return {
        "message": "AI report generation endpoint - NLP integration coming soon",
        "player_id": player_id,
        "status": "pending"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
