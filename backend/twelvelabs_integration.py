"""
Twelve Labs API Integration for ScoutPulse
Provides real video understanding and analysis capabilities
"""
import os
import inspect
import io
import zipfile
import itertools
from typing import List, Dict, Any, Optional, Iterable
from datetime import datetime
import asyncio
import json
from twelvelabs import TwelveLabs
from twelvelabs.indexes import IndexesCreateRequestModelsItem
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()


class TwelveLabsVideoAnalyzer:
    """
    Integration with Twelve Labs API for video understanding
    """
    
    def __init__(self):
        self.api_key = os.getenv("TWELVE_LABS_API_KEY")
        if not self.api_key:
            raise ValueError("TWELVE_LABS_API_KEY not found in environment variables")
        
        self.client = TwelveLabs(api_key=self.api_key)
        self.index_id = os.getenv("TWELVE_LABS_INDEX_ID")
        self.supported_search_options = ["visual", "audio"]

        # Soccer-specific event types
        self.soccer_events = {
            "goal": ["goal", "score", "finish", "shot on target"],
            "assist": ["assist", "pass", "through ball", "cross"],
            "dribble": ["dribble", "run", "beat defender", "skill move"],
            "tackle": ["tackle", "challenge", "win ball"],
            "pass": ["pass", "ball distribution", "play making"],
            "shot": ["shot", "attempt", "strike"],
            "save": ["save", "goalkeeper", "block"],
            "foul": ["foul", "yellow card", "red card"],
            "offside": ["offside", "offside trap"],
            "corner": ["corner kick", "set piece"],
            "free_kick": ["free kick", "direct free kick"]
        }
    
    def _get_default_models(self) -> List[IndexesCreateRequestModelsItem]:
        return [
            IndexesCreateRequestModelsItem(
                model_name="marengo2.7",
                model_options=["visual", "audio"],
            )
        ]

    async def create_index(self, index_name: str = "scoutpulse-soccer") -> str:
        """
        Create a new index for video analysis
        """
        try:
            index = self.client.indexes.create(
                index_name=index_name,
                models=self._get_default_models(),
            )
            self.index_id = index.id
            return index.id
        except Exception as e:
            print(f"Error creating index: {e}")
            # Return existing index if already created
            indexes = self.client.indexes.list()
            for idx in self._iter_sync_pager(indexes):
                idx_name = getattr(idx, "index_name", getattr(idx, "name", None))
                if idx_name == index_name:
                    self.index_id = getattr(idx, "id", None)
                    if self.index_id:
                        return self.index_id
            raise

    async def _ensure_index(self) -> str:
        if self.index_id:
            try:
                self.client.indexes.retrieve(self.index_id)
                return self.index_id
            except Exception as exc:
                print(f"Configured index {self.index_id} not found: {exc}. Creating a new index.")
        return await self.create_index()

    def _iter_sync_pager(self, pager: Iterable) -> Iterable:
        """Normalize SDK pager objects to simple iterables."""
        if hasattr(pager, "data") and isinstance(pager.data, list):
            return pager.data
        if isinstance(pager, list):
            return pager
        return list(pager)

    def _search_query(
        self,
        *,
        index_id: str,
        query_text: str,
        options: Optional[List[str]] = None,
        page_limit: Optional[int] = None,
        filter_params: Optional[Dict[str, Any]] = None,
    ):
        """Call search.query handling SDK signature differences."""
        search_method = self.client.search.query
        signature = inspect.signature(search_method)
        kwargs: Dict[str, Any] = {}

        if "index_id" in signature.parameters:
            kwargs["index_id"] = index_id
        if "query_text" in signature.parameters:
            kwargs["query_text"] = query_text

        if options:
            if "options" in signature.parameters:
                kwargs["options"] = options
            elif "search_options" in signature.parameters:
                kwargs["search_options"] = options

        if page_limit is not None:
            if "page_limit" in signature.parameters:
                kwargs["page_limit"] = page_limit
            elif "limit" in signature.parameters:
                kwargs["limit"] = page_limit
            elif "page_size" in signature.parameters:
                kwargs["page_size"] = page_limit

        if filter_params:
            if "filter" in signature.parameters:
                kwargs["filter"] = filter_params
            elif "filters" in signature.parameters:
                kwargs["filters"] = filter_params

        return search_method(**kwargs)

    async def upload_video(
        self,
        video_title: str,
        player_id: str,
        metadata: Optional[Dict[str, Any]] = None,
        *,
        video_url: Optional[str] = None,
        video_file_path: Optional[Path] = None,
    ) -> str:
        """
        Upload video to Twelve Labs for analysis
        """
        if not video_url and not video_file_path:
            raise ValueError("Either video_url or video_file_path must be provided")

        if video_url and video_file_path:
            raise ValueError("Provide only one of video_url or video_file_path")

        if not self.index_id:
            self.index_id = await self._ensure_index()
        
        try:
            # Create task to index the video
            user_metadata = {
                "player_id": player_id,
                "video_title": video_title,
            }

            if metadata:
                user_metadata.update(metadata)

            if video_file_path:
                with open(video_file_path, 'rb') as video_file:
                    task = self.client.tasks.create(
                        index_id=self.index_id,
                        video_file=video_file,
                        enable_video_stream=True,
                        user_metadata=json.dumps(user_metadata),
                    )
            else:
                task = self.client.tasks.create(
                    index_id=self.index_id,
                    video_url=video_url,
                    enable_video_stream=True,
                    user_metadata=json.dumps(user_metadata),
                )

            completed_task = self.client.tasks.wait_for_done(
                task_id=task.id,
                sleep_interval=5,
            )

            if completed_task.status == "ready":
                return completed_task.video_id
            else:
                raise Exception(f"Video indexing failed with status: {completed_task.status}")
                
        except Exception as e:
            print(f"Error uploading video: {e}")
            raise
    
    async def analyze_video(
        self, 
        video_id: str, 
        player_name: str,
        event_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Analyze video for soccer events and player actions
        """
        if not event_types:
            event_types = list(self.soccer_events.keys())
        
        try:
            detected_events = []
            key_moments = []
            
            # Search for each event type
            for event_type in event_types:
                search_queries = self.soccer_events.get(event_type, [event_type])
                
                for query in search_queries[:2]:  # Limit queries per event
                    # Construct search query with player name
                    search_query = f"{player_name} {query}"
                    
                    # Search in the video
                    search_options = [opt for opt in ["visual", "conversation"] if opt in self.supported_search_options]
                    if not search_options:
                        search_options = ["visual"]

                    search_results = self._search_query(
                        index_id=self.index_id,
                        query_text=search_query,
                        options=search_options,
                        page_limit=5,
                    )

                    # Process results (supporting both clip-level and nested responses)
                    for item in self._iter_sync_pager(search_results):
                        clips = getattr(item, "clips", None)
                        if clips:
                            score = getattr(item, "score", 0)
                            for clip in clips:
                                if score > 70:
                                    detected_events.append({
                                        "type": event_type,
                                        "timestamp": {
                                            "start": clip.start,
                                            "end": clip.end,
                                        },
                                        "confidence": score / 100,
                                        "description": f"{player_name} - {query}",
                                        "video_id": getattr(item, "video_id", None),
                                        "clip_id": getattr(clip, "id", None),
                                    })
                                    key_moments.append({
                                        "time": clip.start,
                                        "description": query,
                                        "importance": score / 100,
                                        "event_type": event_type,
                                    })
                        else:
                            score = getattr(item, "score", 0)
                            if score > 70:
                                detected_events.append({
                                    "type": event_type,
                                    "timestamp": {
                                        "start": getattr(item, "start", 0),
                                        "end": getattr(item, "end", getattr(item, "start", 0) + 5),
                                    },
                                    "confidence": score / 100,
                                    "description": f"{player_name} - {query}",
                                    "video_id": getattr(item, "video_id", None),
                                    "clip_id": getattr(item, "id", None),
                                })
                                key_moments.append({
                                    "time": getattr(item, "start", 0),
                                    "description": query,
                                    "importance": score / 100,
                                    "event_type": event_type,
                                })
            
            # Calculate performance metrics
            performance_metrics = self._calculate_metrics(detected_events)
            
            return {
                "video_id": video_id,
                "analysis_id": f"twelvelabs_{video_id}_{datetime.utcnow().timestamp()}",
                "status": "completed",
                "detected_events": detected_events,
                "key_moments": sorted(key_moments, key=lambda x: x["importance"], reverse=True)[:10],
                "performance_metrics": performance_metrics,
                "total_events": len(detected_events)
            }
            
        except Exception as e:
            print(f"Error analyzing video: {e}")
            raise
    
    async def generate_summary(self, video_id: str, player_name: str) -> str:
        """
        Generate text summary of player performance using Twelve Labs
        """
        try:
            generate_fn = getattr(self.client, "generate_text", None)
            if not generate_fn:
                # Fallback to generic summary if feature unavailable
                return f"Analysis of {player_name}'s performance in the match."

            summary = generate_fn(
                video_id=video_id,
                prompt=f"Provide a detailed analysis of {player_name}'s performance in this match. "
                       f"Focus on: technical skills, tactical awareness, strengths, and areas for improvement."
            )

            return summary
            
        except Exception as e:
            print(f"Error generating summary: {e}")
            return f"Analysis of {player_name}'s performance in the match."
    
    async def extract_highlights(
        self, 
        video_id: str,
        event_types: Optional[List[str]] = None,
        min_confidence: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Extract highlight clips based on detected events
        """
        if not event_types:
            event_types = list(self.soccer_events.keys())
        
        highlights = []
        
        try:
            for event_type in event_types:
                search_queries = self.soccer_events.get(event_type, [event_type])
                
                for query in search_queries[:1]:  # One query per event type
                    search_options = [opt for opt in ["visual"] if opt in self.supported_search_options] or ["visual"]

                    results = self._search_query(
                        index_id=self.index_id,
                        query_text=query,
                        options=search_options,
                        page_limit=3,
                    )
                    
                    for result in results.data:
                        if result.score / 100 >= min_confidence:
                            for clip in result.clips:
                                highlights.append({
                                    "type": event_type,
                                    "timestamp": {
                                        "start": clip.start,
                                        "end": clip.end
                                    },
                                    "confidence": result.score / 100,
                                    "video_id": result.video_id,
                                    "thumbnail_url": clip.thumbnail_url if hasattr(clip, 'thumbnail_url') else None,
                                    "description": query
                                })
            
            return highlights
            
        except Exception as e:
            print(f"Error extracting highlights: {e}")
            return []
    
    async def search_semantic(
        self, 
        query: str,
        video_ids: Optional[List[str]] = None,
        page_limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Semantic search across videos
        """
        try:
            search_options = [opt for opt in ["visual", "conversation", "text_in_video", "audio"] if opt in self.supported_search_options]
            if not search_options:
                search_options = ["visual"]

            results = self._search_query(
                index_id=self.index_id,
                query_text=query,
                options=search_options,
                page_limit=page_limit,
                filter_params={"video_id": video_ids} if video_ids else None,
            )
            
            search_results = []
            for result in results.data:
                for clip in result.clips:
                    search_results.append({
                        "video_id": result.video_id,
                        "score": result.score / 100,
                        "start": clip.start,
                        "end": clip.end,
                        "confidence": result.confidence,
                        "thumbnail_url": clip.thumbnail_url if hasattr(clip, 'thumbnail_url') else None,
                        "metadata": result.metadata if hasattr(result, 'metadata') else {}
                    })
            
            return search_results
            
        except Exception as e:
            print(f"Error in semantic search: {e}")
            return []
    
    def _calculate_metrics(self, events: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculate performance metrics from detected events
        """
        if not events:
            return {
                "success_rate": 0.0,
                "intensity": 0.0,
                "technical_quality": 0.0
            }
        
        # Calculate average confidence as success rate
        avg_confidence = sum(e["confidence"] for e in events) / len(events)
        
        # Intensity based on number of events
        intensity = min(len(events) / 20.0, 1.0)  # Normalize to 0-1
        
        # Technical quality from high-confidence events
        high_conf_events = [e for e in events if e["confidence"] > 0.8]
        technical_quality = len(high_conf_events) / len(events) if events else 0.0
        
        return {
            "success_rate": round(avg_confidence, 2),
            "intensity": round(intensity, 2),
            "technical_quality": round(technical_quality, 2)
        }
    
    async def get_video_info(self, video_id: str) -> Dict[str, Any]:
        """
        Get video information and metadata
        """
        try:
            video = self.client.index.video.get(video_id)
            return {
                "video_id": video.id,
                "duration": video.metadata.duration if hasattr(video.metadata, 'duration') else None,
                "width": video.metadata.width if hasattr(video.metadata, 'width') else None,
                "height": video.metadata.height if hasattr(video.metadata, 'height') else None,
                "status": video.metadata.status if hasattr(video.metadata, 'status') else None
            }
        except Exception as e:
            print(f"Error getting video info: {e}")
            return {}


# Singleton instance
_twelve_labs_analyzer = None


def get_twelve_labs_analyzer() -> TwelveLabsVideoAnalyzer:
    """
    Get or create Twelve Labs analyzer instance
    """
    global _twelve_labs_analyzer
    if _twelve_labs_analyzer is None:
        try:
            _twelve_labs_analyzer = TwelveLabsVideoAnalyzer()
        except ValueError as e:
            print(f"Warning: {e}")
            print("Twelve Labs integration disabled. Set TWELVE_LABS_API_KEY in .env to enable.")
            return None
    return _twelve_labs_analyzer
