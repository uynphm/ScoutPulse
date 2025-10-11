from sqlalchemy.orm import Session
import models
import schemas
from datetime import datetime
import json

def seed_database(db: Session):
    """Seed the database with initial data matching the frontend mock data"""
    
    # Check if data already exists
    if db.query(models.PlayerModel).first():
        print("Database already seeded")
        return
    
    # Seed Players
    players_data = [
        {
            "id": "messi",
            "name": "Lionel Messi",
            "position": "Forward",
            "team": "Barcelona",
            "age": 36,
            "nationality": "Argentina",
            "stats": {
                "dribbling": 95,
                "finishing": 92,
                "passing": 88,
                "defense": 45,
                "speed": 85,
                "strength": 70
            },
            "recent_performance": {
                "goals": 12,
                "assists": 8,
                "average_rating": 8.7,
                "minutes_played": 847
            }
        },
        {
            "id": "ronaldo",
            "name": "Cristiano Ronaldo",
            "position": "Forward",
            "team": "Al Nassr",
            "age": 39,
            "nationality": "Portugal",
            "stats": {
                "dribbling": 88,
                "finishing": 95,
                "passing": 82,
                "defense": 50,
                "speed": 90,
                "strength": 95
            },
            "recent_performance": {
                "goals": 15,
                "assists": 5,
                "average_rating": 8.5,
                "minutes_played": 920
            }
        },
        {
            "id": "mbappe",
            "name": "Kylian Mbappé",
            "position": "Forward",
            "team": "Real Madrid",
            "age": 25,
            "nationality": "France",
            "stats": {
                "dribbling": 90,
                "finishing": 88,
                "passing": 75,
                "defense": 40,
                "speed": 95,
                "strength": 75
            },
            "recent_performance": {
                "goals": 18,
                "assists": 6,
                "average_rating": 8.8,
                "minutes_played": 890
            }
        },
        {
            "id": "haaland",
            "name": "Erling Haaland",
            "position": "Forward",
            "team": "Manchester City",
            "age": 24,
            "nationality": "Norway",
            "stats": {
                "dribbling": 75,
                "finishing": 95,
                "passing": 70,
                "defense": 35,
                "speed": 85,
                "strength": 90
            },
            "recent_performance": {
                "goals": 22,
                "assists": 3,
                "average_rating": 8.9,
                "minutes_played": 780
            }
        }
    ]
    
    for player_data in players_data:
        player = models.PlayerModel(**player_data)
        db.add(player)
    
    # Seed Video Highlights
    highlights_data = [
        {
            "id": "1",
            "title": "Exceptional Dribbling vs Real Madrid",
            "thumbnail": "/api/placeholder/400/225",
            "video_url": "/videos/messi-dribbling-1.mp4",
            "duration": "0:45",
            "match": "Barcelona vs Real Madrid",
            "date": datetime(2024, 3, 15),
            "type": "strength",
            "tags": ["Dribbling", "Ball Control", "Speed"],
            "player_id": "messi",
            "description": "Messi showcases his exceptional dribbling ability, beating multiple defenders in tight spaces.",
            "timestamp": {"start": 120, "end": 165},
            "ai_insights": {
                "confidence": 98,
                "analysis": "Exceptional ball control under pressure with 94% success rate in tight spaces.",
                "key_moments": ["Initial touch", "Change of direction", "Acceleration past defender"]
            }
        },
        {
            "id": "2",
            "title": "Clinical Finishing - Hat Trick Goals",
            "thumbnail": "/api/placeholder/400/225",
            "video_url": "/videos/messi-finishing-1.mp4",
            "duration": "1:20",
            "match": "Barcelona vs Sevilla",
            "date": datetime(2024, 3, 10),
            "type": "strength",
            "tags": ["Finishing", "Positioning", "Shooting"],
            "player_id": "messi",
            "description": "Three clinical finishes showcasing Messi's composure in front of goal.",
            "timestamp": {"start": 45, "end": 125},
            "ai_insights": {
                "confidence": 95,
                "analysis": "Converts 78% of clear chances, significantly above league average of 52%.",
                "key_moments": ["First goal - left foot", "Second goal - right foot", "Third goal - chip"]
            }
        },
        {
            "id": "3",
            "title": "Defensive Positioning Issues",
            "thumbnail": "/api/placeholder/400/225",
            "video_url": "/videos/messi-defense-1.mp4",
            "duration": "0:35",
            "match": "Barcelona vs Atletico",
            "date": datetime(2024, 3, 5),
            "type": "weakness",
            "tags": ["Defense", "Positioning", "Tracking"],
            "player_id": "messi",
            "description": "Examples of defensive positioning that could be improved.",
            "timestamp": {"start": 200, "end": 235},
            "ai_insights": {
                "confidence": 89,
                "analysis": "Limited tracking back with only 1.2 tackles per game, below position average.",
                "key_moments": ["Missed interception", "Poor positioning", "Late tracking"]
            }
        },
        {
            "id": "4",
            "title": "Perfect Through Ball Assists",
            "thumbnail": "/api/placeholder/400/225",
            "video_url": "/videos/messi-passing-1.mp4",
            "duration": "1:05",
            "match": "Barcelona vs Valencia",
            "date": datetime(2024, 2, 28),
            "type": "strength",
            "tags": ["Passing", "Vision", "Assists"],
            "player_id": "messi",
            "description": "Two perfectly weighted through balls leading to goals.",
            "timestamp": {"start": 80, "end": 145},
            "ai_insights": {
                "confidence": 92,
                "analysis": "Creates 4.2 key passes per game with innovative through balls and assists.",
                "key_moments": ["First assist - through ball", "Second assist - lobbed pass"]
            }
        }
    ]
    
    for highlight_data in highlights_data:
        highlight = models.VideoHighlightModel(**highlight_data)
        db.add(highlight)
    
    db.commit()
    print("Database seeded successfully!")

if __name__ == "__main__":
    from database import SessionLocal, engine
    from models import Base
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Seed database
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
