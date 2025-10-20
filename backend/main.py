from fastapi import FastAPI, HTTPException, Depends, Query, WebSocket, WebSocketDisconnect, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional
import os
from pydantic import BaseModel
from datetime import datetime
from dotenv import load_dotenv

from database import get_db, engine
from models import Base, PlayerModel, VideoHighlightModel
from schemas import Player, VideoHighlight, SearchResult, PlayerCreate, VideoHighlightCreate
from crud import (
    get_player_by_id, get_all_players, create_player, delete_player,
    get_highlights, get_highlights_by_player_id, get_highlight_by_id, create_highlight, delete_highlight,
    search_players, search_highlights
)
from ai_services import (
    video_analysis_service,
    semantic_search_service,
    player_report_service,
    analytics_service
)
from websocket_manager import connection_manager, data_notifier
from video_processor import get_video_processor

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
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://localhost:3000",
    "http://127.0.0.1:3000",
    "https://127.0.0.1:3000",
]

LOCAL_NETWORK_ORIGIN = os.getenv("FRONTEND_ORIGIN")
if LOCAL_NETWORK_ORIGIN:
    ALLOWED_ORIGINS.append(LOCAL_NETWORK_ORIGIN)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=r"https?://(?:localhost|127\.0\.0\.1)(?::\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for video serving
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

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
    new_player = create_player(db=db, player=player)
    
    # Notify connected clients
    await data_notifier.notify_player_update(
        new_player.id,
        {
            "id": new_player.id,
            "name": new_player.name,
            "position": new_player.position,
            "team": new_player.team,
            "action": "created"
        }
    )
    
    return new_player


@app.delete("/api/players/{player_id}", status_code=204)
async def delete_existing_player(player_id: str, db: Session = Depends(get_db)):
    """Delete a player and their associated highlights."""
    if not delete_player(db, player_id):
        raise HTTPException(status_code=404, detail="Player not found")

    await data_notifier.notify_player_update(player_id, {"id": player_id, "action": "deleted"})
    return None

# Video highlight endpoints
@app.get("/api/highlights", response_model=List[VideoHighlight])
async def list_highlights(
    player_id: Optional[str] = Query(None),
    highlight_type: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get video highlights with optional filtering"""
    return get_highlights(
        db,
        player_id=player_id,
        highlight_type=highlight_type,
        skip=skip,
        limit=limit,
    )

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
    new_highlight = create_highlight(db=db, highlight=highlight)
    
    # Notify connected clients
    await data_notifier.notify_highlight_added({
        "id": new_highlight.id,
        "title": new_highlight.title,
        "player_id": new_highlight.player_id,
        "type": new_highlight.type,
        "thumbnail": new_highlight.thumbnail,
        "action": "created"
    })
    
    return new_highlight


@app.delete("/api/highlights/{highlight_id}", status_code=204)
async def delete_existing_highlight(highlight_id: str, db: Session = Depends(get_db)):
    """Delete a specific highlight."""
    if not delete_highlight(db, highlight_id):
        raise HTTPException(status_code=404, detail="Highlight not found")

    return None

# Search endpoints
@app.get("/api/search", response_model=List[SearchResult])
async def search(
    q: str = Query(..., min_length=1),
    search_type: Optional[str] = Query("all", pattern="^(all|players|highlights)$"),
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
                relevance_score=0.9
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
                relevance_score=0.8
            )
            for highlight in highlights
        ])
    
    return results

@app.get("/api/search/semantic")
async def semantic_search(
    q: str = Query(..., min_length=1),
    player_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Natural language semantic search for highlights"""
    try:
        results = await semantic_search_service.search_highlights(db, q, player_id)
        return {
            "query": q,
            "parsed_query": semantic_search_service.parse_query(q),
            "results": [
                {
                    "id": r["highlight"].id,
                    "title": r["highlight"].title,
                    "description": r["highlight"].description,
                    "video_url": r["highlight"].video_url,
                    "thumbnail": r["highlight"].thumbnail,
                    "type": r["highlight"].type,
                    "relevance_score": r["relevance_score"],
                    "matched_terms": r["matched_terms"],
                    "timestamp": r["highlight"].timestamp,
                    "ai_insights": r["highlight"].ai_insights
                }
                for r in results[:20]  # Top 20 results
            ],
            "total_results": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

# AI Analysis endpoints
@app.post("/api/analyze-video")
async def analyze_video(
    video_url: str,
    player_id: str,
    db: Session = Depends(get_db)
):
    """Analyze video for AI insights and event detection"""
    try:
        # Verify player exists
        player = get_player_by_id(db, player_id=player_id)
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        
        # Perform AI video analysis with Twelve Labs
        analysis_result = await video_analysis_service.analyze_video(
            video_url, 
            player_id,
            player_name=player.name
        )
        
        # Index content for semantic search
        indexed_content = video_analysis_service.index_video_content(analysis_result)
        
        # Notify connected clients
        await data_notifier.notify_analysis_complete(
            analysis_result["analysis_id"],
            player_id,
            {
                "detected_events": len(analysis_result.get("detected_events", [])),
                "key_moments": len(analysis_result.get("key_moments", [])),
                "status": "completed"
            }
        )
        
        return {
            "status": "success",
            "analysis": analysis_result,
            "indexed_content": indexed_content,
            "message": "Video analyzed successfully. Events detected and indexed for search."
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/api/extract-highlights")
async def extract_highlights(
    video_url: str,
    video_id: Optional[str] = None,
    event_types: Optional[List[str]] = None
):
    """Extract highlight clips from full match video"""
    try:
        highlights = await video_analysis_service.extract_highlights(
            video_url, 
            video_id=video_id,
            event_types=event_types
        )
        return {
            "status": "success",
            "video_url": video_url,
            "highlights": highlights,
            "count": len(highlights)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")

class ProcessVideoRequest(BaseModel):
    video_url: str
    player_id: str
    match_name: str
    match_date: datetime
    auto_create_highlights: bool = True


@app.post("/api/process-video")
async def process_video(
    payload: ProcessVideoRequest | None = Body(None),
    video_url: Optional[str] = Query(None),
    player_id: Optional[str] = Query(None),
    match_name: Optional[str] = Query(None),
    match_date: Optional[str] = Query(None),
    auto_create_highlights: bool = Query(True),
    db: Session = Depends(get_db)
):
    """
    Complete video processing workflow:
    1. Upload video to Twelve Labs
    2. Analyze for soccer events
    3. Automatically create highlights in database
    
    This is the main endpoint to use for processing new match videos.
    """
    try:
        # Derive payload from query params when JSON body omitted
        if payload is None:
            if not all([video_url, player_id, match_name, match_date]):
                raise HTTPException(status_code=422, detail="Missing video processing parameters")

            try:
                match_date_parsed = datetime.fromisoformat(match_date)  # type: ignore[arg-type]
            except Exception:
                match_date_parsed = datetime.utcnow()

            payload = ProcessVideoRequest(
                video_url=video_url,  # type: ignore[arg-type]
                player_id=player_id,  # type: ignore[arg-type]
                match_name=match_name,  # type: ignore[arg-type]
                match_date=match_date_parsed,
                auto_create_highlights=auto_create_highlights,
            )

        # Get video processor
        processor = get_video_processor()
        
        # Process video
        result = await processor.process_video_for_player(
            db=db,
            video_url=payload.video_url,
            player_id=payload.player_id,
            match_name=payload.match_name,
            match_date=payload.match_date,
            auto_create_highlights=payload.auto_create_highlights
        )
        
        # Notify connected clients
        await data_notifier.notify_highlight_added({
            "player_id": payload.player_id,
            "highlights_count": result["highlights_created"],
            "action": "video_processed"
        })
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video processing failed: {str(e)}")

@app.post("/api/extract-and-save-highlights")
async def extract_and_save_highlights(
    video_id: str,
    player_id: str,
    match_name: str,
    match_date: str,
    event_types: Optional[List[str]] = None,
    min_confidence: float = Query(0.7, ge=0.0, le=1.0),
    db: Session = Depends(get_db)
):
    """
    Extract highlights from an already-indexed video and save to database.
    Use this if you've already uploaded a video to Twelve Labs.
    """
    try:
        from datetime import datetime
        
        # Parse match date
        try:
            match_date_obj = datetime.fromisoformat(match_date)
        except:
            match_date_obj = datetime.utcnow()
        
        processor = get_video_processor()
        
        highlights = await processor.extract_and_save_highlights(
            db=db,
            video_id=video_id,
            player_id=player_id,
            match_name=match_name,
            match_date=match_date_obj,
            event_types=event_types,
            min_confidence=min_confidence
        )
        
        return {
            "status": "success",
            "video_id": video_id,
            "highlights_created": len(highlights),
            "highlights": highlights
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Highlight extraction failed: {str(e)}")

@app.post("/api/generate-report/{player_id}")
async def generate_player_report(
    player_id: str,
    include_video_analysis: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Generate comprehensive AI-powered player report"""
    try:
        report = await player_report_service.generate_report(
            db, 
            player_id, 
            include_video_analysis
        )
        
        # Notify connected clients
        await data_notifier.notify_report_generated(
            report["report_id"],
            player_id
        )
        
        return report
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")

@app.get("/api/reports/{player_id}")
async def get_player_report(
    player_id: str,
    db: Session = Depends(get_db)
):
    """Get or generate player report"""
    return await generate_player_report(player_id, True, db)

# Analytics endpoints
@app.get("/api/analytics/player/{player_id}")
async def get_player_analytics(
    player_id: str,
    db: Session = Depends(get_db)
):
    """Get comprehensive analytics for a player"""
    try:
        analytics = await analytics_service.get_player_analytics(db, player_id)
        return analytics
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics failed: {str(e)}")

@app.get("/api/analytics/global")
async def get_global_statistics(db: Session = Depends(get_db)):
    """Get global statistics across all players and highlights"""
    try:
        stats = await analytics_service.get_global_statistics(db)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Statistics failed: {str(e)}")

@app.get("/api/stats/count")
async def count_data(
    entity: str = Query(..., pattern="^(players|highlights|all)$"),
    player_id: Optional[str] = Query(None),
    highlight_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Count players, highlights, or specific data"""
    try:
        result = {"entity": entity}
        
        if entity in ["players", "all"]:
            result["total_players"] = db.query(PlayerModel).count()
        
        if entity in ["highlights", "all"]:
            query = db.query(VideoHighlightModel)
            
            if player_id:
                query = query.filter(VideoHighlightModel.player_id == player_id)
            if highlight_type and highlight_type != "all":
                query = query.filter(VideoHighlightModel.type == highlight_type)
            
            result["total_highlights"] = query.count()
            
            if not player_id and not highlight_type:
                # Breakdown by type
                result["by_type"] = {
                    "strength": db.query(VideoHighlightModel).filter(
                        VideoHighlightModel.type == "strength"
                    ).count(),
                    "weakness": db.query(VideoHighlightModel).filter(
                        VideoHighlightModel.type == "weakness"
                    ).count(),
                    "neutral": db.query(VideoHighlightModel).filter(
                        VideoHighlightModel.type == "neutral"
                    ).count()
                }
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Count failed: {str(e)}")

# WebSocket endpoints for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Global WebSocket endpoint for all updates"""
    await connection_manager.connect(websocket, "global")
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            # Echo back for heartbeat
            await websocket.send_json({"type": "pong", "message": "connected"})
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket, "global")

@app.websocket("/ws/player/{player_id}")
async def player_websocket(websocket: WebSocket, player_id: str):
    """Player-specific WebSocket for real-time player updates"""
    await connection_manager.connect_player_channel(websocket, player_id)
    try:
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connected",
            "player_id": player_id,
            "message": f"Connected to player {player_id} updates"
        })
        
        while True:
            data = await websocket.receive_text()
            await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        connection_manager.disconnect_player_channel(websocket, player_id)

@app.websocket("/ws/highlights")
async def highlights_websocket(websocket: WebSocket):
    """WebSocket for highlight updates"""
    await connection_manager.connect(websocket, "highlights")
    try:
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to highlights updates"
        })
        
        while True:
            data = await websocket.receive_text()
            await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket, "highlights")

@app.websocket("/ws/analytics")
async def analytics_websocket(websocket: WebSocket):
    """WebSocket for analytics and statistics updates"""
    await connection_manager.connect(websocket, "analytics")
    try:
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to analytics updates"
        })
        
        while True:
            data = await websocket.receive_text()
            await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket, "analytics")

@app.get("/api/ws/status")
async def websocket_status():
    """Get WebSocket connection status"""
    return {
        "total_connections": connection_manager.get_connection_count(),
        "connections_by_channel": {
            "global": connection_manager.get_connection_count("global"),
            "players": connection_manager.get_connection_count("players"),
            "highlights": connection_manager.get_connection_count("highlights"),
            "analytics": connection_manager.get_connection_count("analytics")
        },
        "player_channels": len(connection_manager.player_connections)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
