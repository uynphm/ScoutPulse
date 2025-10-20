import os
import sys
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from models import SessionLocal, Base, engine
from crud import create_player, get_player_by_id
from schemas import PlayerCreate, PlayerStats, RecentPerformance

load_dotenv()

def main():
    db = SessionLocal()
    try:
        Base.metadata.create_all(bind=engine)

        existing = get_player_by_id(db, "test-player")
        if existing:
            print("test-player already exists. Skipping seed.")
            return

        player = PlayerCreate(
            id="test-player",
            name="Test Player",
            position="Forward",
            team="Test FC",
            age=22,
            nationality="USA",
            avatar=None,
            stats=PlayerStats(
                dribbling=85,
                finishing=88,
                passing=82,
                defense=60,
                speed=90,
                strength=78,
            ),
            recent_performance=RecentPerformance(
                goals=5,
                assists=3,
                average_rating=7.8,
                minutes_played=540,
            ),
        )
        create_player(db, player)
        print("Seeded test-player successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
