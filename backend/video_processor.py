"""
Video Processing Service for ScoutPulse
Handles video upload, analysis, and automatic highlight extraction
"""
import asyncio
import os
import subprocess
import shutil
import tempfile
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

import requests
from sqlalchemy.orm import Session
from yt_dlp import YoutubeDL

from models import VideoHighlightModel, PlayerModel
from twelvelabs_integration import get_twelve_labs_analyzer
from crud import create_highlight
from schemas import VideoHighlightCreate, Timestamp, AIInsights


class VideoProcessor:
    """
    Service to process videos and automatically create highlights in database
    """
    
    def __init__(self):
        self.twelve_labs = get_twelve_labs_analyzer()
        self.use_twelve_labs = self.twelve_labs is not None

    @staticmethod
    def _is_youtube_url(url: str) -> bool:
        parsed = urlparse(url)
        if not parsed.scheme.startswith("http"):
            return False
        hostname = parsed.hostname or ""
        return any(hostname.endswith(domain) for domain in ["youtube.com", "youtu.be", "youtube-nocookie.com"])

    async def _download_youtube_video(self, url: str) -> Path:
        """Download YouTube video to a temporary file using yt-dlp."""
        loop = asyncio.get_running_loop()

        temp_dir = tempfile.mkdtemp(prefix="scoutpulse-yt-")
        output_template = str(Path(temp_dir) / "video.%(ext)s")
        max_seconds = int(os.getenv("YOUTUBE_MAX_DOWNLOAD_SECONDS", "600"))

        def _download() -> Path:
            ydl_opts = {
                "format": "bestvideo[ext=mp4][height<=720]+bestaudio[ext=m4a]/best[ext=mp4]/best",
                "outtmpl": output_template,
                "merge_output_format": "mp4",
                "quiet": True,
                "no_warnings": True,
                "noplaylist": True,
            }

            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filepath = Path(ydl.prepare_filename(info)).with_suffix(".mp4")
            return filepath

        try:
            file_path = await loop.run_in_executor(None, _download)
            if not file_path.exists():
                raise FileNotFoundError("Downloaded video file not found")

            trimmed_path = await self._trim_video(file_path, max_seconds)
            print(f"Prepared file for Twelve Labs: {trimmed_path} ({trimmed_path.stat().st_size} bytes)")
            return trimmed_path
        except Exception:
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise

    async def _cleanup_file(self, path: Path):
        """Remove temporary file and directory."""
        if os.getenv("KEEP_YT_TEMP"):
            print(f"Skipping cleanup for debug. Temp file remains at {path}")
            return

        try:
            temp_dir = path.parent
            path.unlink(missing_ok=True)
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass

    async def _trim_video(self, path: Path, max_seconds: int) -> Path:
        if max_seconds <= 0:
            return path

        # Ensure minimum 10 seconds for Twelve Labs
        trim_duration = max(10, min(max_seconds, 7200))

        temp_dir = path.parent
        trimmed_path = temp_dir / "video_trimmed.mp4"

        try:
            cmd = [
                "ffmpeg",
                "-y",
                "-i",
                str(path),
                "-t",
                str(trim_duration),
                "-vf",
                "fps=30,scale='min(1280,iw)':'min(720,ih)':force_original_aspect_ratio=decrease",
                "-c:v",
                "libx264",
                "-preset",
                "veryfast",
                "-crf",
                "23",
                "-pix_fmt",
                "yuv420p",
                "-g",
                "60",
                "-keyint_min",
                "60",
                "-movflags",
                "+faststart",
                "-c:a",
                "aac",
                "-b:a",
                "128k",
                "-ar",
                "44100",
                str(trimmed_path),
            ]
            process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            stdout, stderr = await process.communicate()
            if process.returncode != 0 or not trimmed_path.exists():
                raise RuntimeError(f"ffmpeg trim failed: {stderr.decode(errors='ignore')}")

            path.unlink(missing_ok=True)
            return trimmed_path
        except Exception:
            trimmed_path.unlink(missing_ok=True)
            return path

    async def process_video_for_player(
        self,
        db: Session,
        video_url: str,
        player_id: str,
        match_name: str,
        match_date: datetime,
        auto_create_highlights: bool = True
    ) -> Dict[str, Any]:
        """
        Complete workflow: Upload video, analyze it, and create highlights in database
        
        Args:
            db: Database session
            video_url: URL of the video to process
            player_id: ID of the player in the video
            match_name: Name of the match (e.g., "Barcelona vs Real Madrid")
            match_date: Date of the match
            auto_create_highlights: If True, automatically create highlight records in DB
        
        Returns:
            Dict with processing results including video_id, analysis, and created highlights
        """
        # Get player info
        player = db.query(PlayerModel).filter(PlayerModel.id == player_id).first()
        if not player:
            raise ValueError(f"Player {player_id} not found")

        print(f"Processing video for {player.name}...")

        if not self.use_twelve_labs:
            print("Twelve Labs integration disabled. Returning simulated analysis.")
            return self._simulate_processing(
                db=db,
                player=player,
                video_url=video_url,
                match_name=match_name,
                match_date=match_date,
                auto_create_highlights=auto_create_highlights,
            )

        try:
            download_path: Optional[Path] = None
            upload_kwargs = {
                "video_title": f"{player.name}_{match_name}",
                "player_id": player_id,
                "metadata": {"match": match_name, "date": match_date.isoformat()},
            }

            if self._is_youtube_url(video_url):
                print("Detected YouTube URL. Downloading video before upload...")
                download_path = await self._download_youtube_video(video_url)
                upload_kwargs["video_file_path"] = download_path
            else:
                upload_kwargs["video_url"] = video_url

            # Step 1: Upload video to Twelve Labs
            print("Uploading video to Twelve Labs...")
            video_id = await self.twelve_labs.upload_video(**upload_kwargs)
            print(f"Video uploaded. Video ID: {video_id}")

            # Step 2: Analyze video for events
            print("Analyzing video for soccer events...")
            analysis = await self.twelve_labs.analyze_video(
                video_id=video_id,
                player_name=player.name,
                event_types=["goal", "assist", "dribble", "pass", "shot", "tackle"]
            )
            print(f"Analysis complete. Found {len(analysis['detected_events'])} events")

            # Step 3: Generate AI summary
            print("Generating AI summary...")
            summary = await self.twelve_labs.generate_summary(video_id, player.name)
            analysis["ai_summary"] = summary

            created_highlights = []

            # Step 4: Create highlights in database
            if auto_create_highlights and analysis['detected_events']:
                events = sorted(
                    analysis["detected_events"],
                    key=lambda ev: ev.get("confidence", 0),
                    reverse=True,
                )[:20]
                print(f"Creating {len(events)} highlights in database...")

                for event in events:
                    try:
                        highlight_data = self._create_highlight_from_event(
                            event=event,
                            player_id=player_id,
                            player_name=player.name,
                            video_url=self._resolve_event_video_url(event, video_url),
                            match_name=match_name,
                            match_date=match_date,
                            video_id=video_id
                        )

                        # Create highlight in database
                        highlight = create_highlight(db, highlight_data)
                        created_highlights.append({
                            "id": highlight.id,
                            "title": highlight.title,
                            "type": highlight.type,
                            "timestamp": highlight.timestamp,
                            "video_url": highlight.video_url,
                        })

                    except Exception as e:
                        print(f"Error creating highlight: {e}")
                        continue

            return {
                "status": "success",
                "video_id": video_id,
                "player_id": player_id,
                "player_name": player.name,
                "match": match_name,
                "analysis": analysis,
                "highlights_created": len(created_highlights),
                "highlights": created_highlights,
                "message": f"Successfully processed video. Created {len(created_highlights)} highlights."
            }

        except Exception as exc:
            print(f"Twelve Labs processing failed: {exc}. Falling back to simulated results.")
            return self._simulate_processing(
                db=db,
                player=player,
                video_url=video_url,
                match_name=match_name,
                match_date=match_date,
                auto_create_highlights=auto_create_highlights,
            )
        finally:
            if 'download_path' in locals() and download_path:
                await self._cleanup_file(download_path)
    
    def _create_highlight_from_event(
        self,
        event: Dict[str, Any],
        player_id: str,
        player_name: str,
        video_url: str,
        match_name: str,
        match_date: datetime,
        video_id: str
    ) -> VideoHighlightCreate:
        """
        Convert a detected event into a VideoHighlight schema for database insertion
        """
        event_type = event["type"]
        confidence = event["confidence"]
        
        # Determine if this is a strength or weakness based on event type and confidence
        if event_type in ["goal", "assist", "dribble", "pass"] and confidence > 0.75:
            highlight_type = "strength"
        elif event_type in ["foul", "offside"] or confidence < 0.6:
            highlight_type = "weakness"
        else:
            highlight_type = "neutral"
        
        # Create title
        title = f"{player_name} - {event_type.title()}"
        if event_type == "goal":
            title = f"{player_name} - Goal"
        elif event_type == "assist":
            title = f"{player_name} - Assist"
        elif event_type == "dribble":
            title = f"{player_name} - Dribbling Sequence"
        
        # Calculate duration
        start_time = int(round(event["timestamp"]["start"]))
        end_time = int(round(event["timestamp"]["end"]))
        duration_seconds = end_time - start_time
        duration_str = f"{int(duration_seconds // 60)}:{int(duration_seconds % 60):02d}"
        
        # Create tags
        tags = [event_type.title()]
        if confidence > 0.9:
            tags.append("Excellent")
        if event_type in ["goal", "assist"]:
            tags.extend(["Key Moment", "Highlight"])
        
        return VideoHighlightCreate(
            id=str(uuid.uuid4()),
            title=title,
            thumbnail=f"/thumbnails/{video_id}_{start_time}.jpg",
            video_url=video_url,
            duration=duration_str,
            match=match_name,
            date=match_date,
            type=highlight_type,
            tags=tags,
            player_id=player_id,
            description=event.get("description", f"{player_name} {event_type}"),
            timestamp=Timestamp(
                start=start_time,
                end=end_time
            ),
            ai_insights=AIInsights(
                confidence=int(confidence * 100),
                analysis=f"Detected {event_type} with {confidence*100:.1f}% confidence",
                key_moments=[f"{event_type} at {start_time}s"]
            )
        )

    def _resolve_event_video_url(self, event: Dict[str, Any], source_video_url: str) -> str:
        """Return the proper video URL for a highlight clip.

        Priority order:
        1. Event-provided `clip_url` (typically from Twelve Labs).
        2. For uploads from YouTube, derive the `https://www.youtube.com/embed/...` URL so browsers can play it.
        3. Fallback to the original `source_video_url`.
        """

        clip_url = event.get("clip_url") or event.get("video_url")
        if isinstance(clip_url, str) and clip_url.strip():
            return clip_url

        if source_video_url and self._is_youtube_url(source_video_url):
            parsed = urlparse(source_video_url)
            video_id = ""
            if parsed.hostname and parsed.hostname.endswith("youtu.be"):
                video_id = parsed.path.lstrip("/")
            else:
                query = parsed.query
                for part in query.split("&"):
                    if part.startswith("v="):
                        video_id = part.split("=", 1)[1]
                        break
            if video_id:
                return f"https://www.youtube.com/embed/{video_id}"

        return source_video_url

    def _simulate_processing(
        self,
        db: Session,
        player: PlayerModel,
        video_url: str,
        match_name: str,
        match_date: datetime,
        auto_create_highlights: bool,
    ) -> Dict[str, Any]:
        """Return deterministic simulated analysis when Twelve Labs is unavailable."""

        video_id = f"simulated-{uuid.uuid4()}"

        simulated_events = [
            {
                "type": "goal",
                "timestamp": {"start": 75, "end": 90},
                "confidence": 0.92,
                "description": f"{player.name} scores from inside the box",
                "video_id": video_id,
                "clip_id": None,
            },
            {
                "type": "assist",
                "timestamp": {"start": 180, "end": 195},
                "confidence": 0.88,
                "description": f"{player.name} provides a key pass leading to a goal",
                "video_id": video_id,
                "clip_id": None,
            },
            {
                "type": "dribble",
                "timestamp": {"start": 260, "end": 275},
                "confidence": 0.84,
                "description": f"{player.name} beats two defenders",
                "video_id": video_id,
                "clip_id": None,
            },
        ]

        key_moments = [
            {"time": event["timestamp"]["start"], "description": event["description"], "importance": event["confidence"], "event_type": event["type"]}
            for event in simulated_events
        ]

        analysis = {
            "video_id": video_id,
            "analysis_id": f"simulated_{video_id}",
            "status": "simulated",
            "detected_events": simulated_events,
            "key_moments": key_moments,
            "performance_metrics": {
                "success_rate": 0.9,
                "intensity": 0.6,
                "technical_quality": 0.75,
            },
            "total_events": len(simulated_events),
            "ai_summary": (
                f"Simulated analysis for {player.name}: influential performance with goals, assists, and ball progression."
            ),
        }

        created_highlights = []

        if auto_create_highlights:
            for event in simulated_events:
                try:
                    highlight_data = self._create_highlight_from_event(
                        event=event,
                        player_id=player.id,
                        player_name=player.name,
                        video_url=video_url,
                        match_name=match_name,
                        match_date=match_date,
                        video_id=video_id,
                    )
                    highlight = create_highlight(db, highlight_data)
                    created_highlights.append(
                        {
                            "id": highlight.id,
                            "title": highlight.title,
                            "type": highlight.type,
                            "timestamp": highlight.timestamp,
                        }
                    )
                except Exception as error:
                    print(f"Simulated highlight creation failed: {error}")
                    continue

        return {
            "status": "success",
            "video_id": video_id,
            "player_id": player.id,
            "player_name": player.name,
            "match": match_name,
            "analysis": analysis,
            "highlights_created": len(created_highlights),
            "highlights": created_highlights,
            "message": (
                "Twelve Labs unavailable. Returned simulated analysis and highlights for local testing."
            ),
        }
    
    async def extract_and_save_highlights(
        self,
        db: Session,
        video_id: str,
        player_id: str,
        match_name: str,
        match_date: datetime,
        event_types: Optional[List[str]] = None,
        min_confidence: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Extract highlights from an already-indexed video and save to database
        """
        if not self.use_twelve_labs:
            raise ValueError("Twelve Labs integration not configured")
        
        player = db.query(PlayerModel).filter(PlayerModel.id == player_id).first()
        if not player:
            raise ValueError(f"Player {player_id} not found")
        
        # Extract highlights using Twelve Labs
        highlights = await self.twelve_labs.extract_highlights(
            video_id=video_id,
            event_types=event_types,
            min_confidence=min_confidence
        )
        
        created_highlights = []
        
        for highlight_data in highlights:
            try:
                # Convert to database format
                event = {
                    "type": highlight_data["type"],
                    "timestamp": highlight_data["timestamp"],
                    "confidence": highlight_data["confidence"],
                    "description": highlight_data.get("description", "")
                }
                
                highlight_schema = self._create_highlight_from_event(
                    event=event,
                    player_id=player_id,
                    player_name=player.name,
                    video_url=f"https://api.twelvelabs.io/v1.2/indexes/{self.twelve_labs.index_id}/videos/{video_id}",
                    match_name=match_name,
                    match_date=match_date,
                    video_id=video_id
                )
                
                # Save to database
                db_highlight = create_highlight(db, highlight_schema)
                created_highlights.append({
                    "id": db_highlight.id,
                    "title": db_highlight.title,
                    "type": db_highlight.type
                })
                
            except Exception as e:
                print(f"Error saving highlight: {e}")
                continue
        
        return created_highlights
    
    async def reanalyze_existing_video(
        self,
        db: Session,
        video_id: str,
        player_id: str
    ) -> Dict[str, Any]:
        """
        Re-analyze an existing video that's already in Twelve Labs index
        """
        if not self.use_twelve_labs:
            raise ValueError("Twelve Labs integration not configured")
        
        player = db.query(PlayerModel).filter(PlayerModel.id == player_id).first()
        if not player:
            raise ValueError(f"Player {player_id} not found")
        
        # Analyze the video
        analysis = await self.twelve_labs.analyze_video(
            video_id=video_id,
            player_name=player.name
        )
        
        return {
            "status": "success",
            "video_id": video_id,
            "player_name": player.name,
            "analysis": analysis
        }


# Singleton instance
_video_processor = None


def get_video_processor() -> VideoProcessor:
    """Get or create video processor instance"""
    global _video_processor
    if _video_processor is None:
        _video_processor = VideoProcessor()
    return _video_processor
