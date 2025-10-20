from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import models
import schemas

# Player CRUD operations
def get_player_by_id(db: Session, player_id: str) -> Optional[models.PlayerModel]:
    return db.query(models.PlayerModel).filter(models.PlayerModel.id == player_id).first()

def get_all_players(db: Session, skip: int = 0, limit: int = 100) -> List[models.PlayerModel]:
    return db.query(models.PlayerModel).offset(skip).limit(limit).all()

def create_player(db: Session, player: schemas.PlayerCreate) -> models.PlayerModel:
    db_player = models.PlayerModel(
        id=player.id,
        name=player.name,
        position=player.position,
        team=player.team,
        age=player.age,
        nationality=player.nationality,
        avatar=player.avatar,
        stats=player.stats.dict(),
        recent_performance=player.recent_performance.dict()
    )
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player

def search_players(db: Session, query: str) -> List[models.PlayerModel]:
    """Search players by name, team, position, or nationality"""
    search_term = f"%{query.lower()}%"
    return db.query(models.PlayerModel).filter(
        models.PlayerModel.name.ilike(search_term) |
        models.PlayerModel.team.ilike(search_term) |
        models.PlayerModel.position.ilike(search_term) |
        models.PlayerModel.nationality.ilike(search_term)
    ).all()

# Video Highlight CRUD operations
def get_highlight_by_id(db: Session, highlight_id: str) -> Optional[models.VideoHighlightModel]:
    return db.query(models.VideoHighlightModel).filter(models.VideoHighlightModel.id == highlight_id).first()

def get_highlights_by_player_id(db: Session, player_id: str) -> List[models.VideoHighlightModel]:
    return db.query(models.VideoHighlightModel).filter(models.VideoHighlightModel.player_id == player_id).all()

def get_all_highlights(db: Session, skip: int = 0, limit: int = 100) -> List[models.VideoHighlightModel]:
    return db.query(models.VideoHighlightModel).offset(skip).limit(limit).all()

def get_highlights(
    db: Session,
    *,
    player_id: Optional[str] = None,
    highlight_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[models.VideoHighlightModel]:
    query = db.query(models.VideoHighlightModel)

    if player_id:
        query = query.filter(models.VideoHighlightModel.player_id == player_id)

    if highlight_type and highlight_type != "all":
        query = query.filter(models.VideoHighlightModel.type == highlight_type)

    return query.offset(skip).limit(limit).all()

def create_highlight(db: Session, highlight: schemas.VideoHighlightCreate) -> models.VideoHighlightModel:
    db_highlight = models.VideoHighlightModel(
        id=highlight.id,
        title=highlight.title,
        thumbnail=highlight.thumbnail,
        video_url=highlight.video_url,
        duration=highlight.duration,
        match=highlight.match,
        date=highlight.date,
        type=highlight.type,
        tags=highlight.tags,
        player_id=highlight.player_id,
        description=highlight.description,
        timestamp=highlight.timestamp.dict(),
        ai_insights=highlight.ai_insights.dict()
    )
    db.add(db_highlight)
    db.commit()
    db.refresh(db_highlight)
    return db_highlight


def delete_highlight(db: Session, highlight_id: str) -> bool:
    highlight = get_highlight_by_id(db, highlight_id)
    if not highlight:
        return False

    db.delete(highlight)
    db.commit()
    return True


def delete_player(db: Session, player_id: str) -> bool:
    player = get_player_by_id(db, player_id)
    if not player:
        return False

    # Remove associated highlights first
    db.query(models.VideoHighlightModel).filter(models.VideoHighlightModel.player_id == player_id).delete(synchronize_session=False)
    db.delete(player)
    db.commit()
    return True

def search_highlights(db: Session, query: str) -> List[models.VideoHighlightModel]:
    """Search highlights by title, match, tags, or description"""
    search_term = f"%{query.lower()}%"
    return db.query(models.VideoHighlightModel).filter(
        models.VideoHighlightModel.title.ilike(search_term) |
        models.VideoHighlightModel.match.ilike(search_term) |
        models.VideoHighlightModel.description.ilike(search_term)
    ).all()

def filter_highlights_by_type(db: Session, highlight_type: str) -> List[models.VideoHighlightModel]:
    """Filter highlights by type (strength, weakness, neutral)"""
    if highlight_type == "all":
        return get_all_highlights(db)
    return db.query(models.VideoHighlightModel).filter(models.VideoHighlightModel.type == highlight_type).all()

def filter_highlights_by_date_range(db: Session, start_date: datetime, end_date: datetime) -> List[models.VideoHighlightModel]:
    """Filter highlights by date range"""
    return db.query(models.VideoHighlightModel).filter(
        models.VideoHighlightModel.date >= start_date,
        models.VideoHighlightModel.date <= end_date
    ).all()
