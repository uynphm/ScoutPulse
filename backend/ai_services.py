"""
AI Services for ScoutPulse
Handles video analysis, semantic search, and NLP report generation
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import re
from sqlalchemy.orm import Session
from models import VideoHighlightModel, PlayerModel
from twelvelabs_integration import get_twelve_labs_analyzer


class VideoAnalysisService:
    """
    Service for AI-powered video analysis
    Integrates with Twelve Labs video understanding API
    """
    
    def __init__(self):
        self.supported_events = [
            "goal", "assist", "shot", "pass", "dribble", "tackle",
            "interception", "clearance", "save", "foul", "offside"
        ]
        self.twelve_labs = get_twelve_labs_analyzer()
        self.use_twelve_labs = self.twelve_labs is not None
    
    async def analyze_video(self, video_url: str, player_id: str, player_name: str = None) -> Dict[str, Any]:
        """
        Analyze video for player actions and events using Twelve Labs API
        Returns structured data about detected events
        """
        if self.use_twelve_labs and player_name:
            try:
                # Upload video to Twelve Labs
                video_id = await self.twelve_labs.upload_video(
                    video_url=video_url,
                    video_title=f"{player_name}_match_analysis",
                    player_id=player_id
                )
                
                # Analyze video for soccer events
                analysis = await self.twelve_labs.analyze_video(
                    video_id=video_id,
                    player_name=player_name,
                    event_types=self.supported_events
                )
                
                # Add video URL to result
                analysis["video_url"] = video_url
                analysis["player_id"] = player_id
                
                return analysis
                
            except Exception as e:
                print(f"Twelve Labs API error: {e}. Falling back to mock data.")
        
        # Fallback to mock data if Twelve Labs not available
        analysis_result = {
            "video_url": video_url,
            "player_id": player_id,
            "analysis_id": f"analysis_{datetime.utcnow().timestamp()}",
            "status": "completed",
            "detected_events": [
                {
                    "type": "dribble",
                    "timestamp": {"start": 120, "end": 135},
                    "confidence": 0.95,
                    "description": "Successful dribble past defender"
                },
                {
                    "type": "pass",
                    "timestamp": {"start": 140, "end": 145},
                    "confidence": 0.92,
                    "description": "Through ball to teammate"
                }
            ],
            "key_moments": [
                {"time": 125, "description": "Change of direction", "importance": 0.9},
                {"time": 142, "description": "Vision and execution", "importance": 0.85}
            ],
            "performance_metrics": {
                "success_rate": 0.87,
                "intensity": 0.92,
                "technical_quality": 0.89
            }
        }
        
        return analysis_result
    
    async def extract_highlights(
        self, 
        video_url: str, 
        video_id: str = None,
        event_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Extract specific highlight clips from full match video using Twelve Labs
        """
        if event_types is None:
            event_types = self.supported_events
        
        if self.use_twelve_labs and video_id:
            try:
                # Use Twelve Labs to extract highlights
                highlights = await self.twelve_labs.extract_highlights(
                    video_id=video_id,
                    event_types=event_types,
                    min_confidence=0.7
                )
                return highlights
                
            except Exception as e:
                print(f"Twelve Labs API error: {e}. Falling back to mock data.")
        
        # Fallback to mock data
        highlights = []
        for event_type in event_types[:3]:  # Mock 3 highlights
            highlights.append({
                "type": event_type,
                "timestamp": {"start": 100, "end": 120},
                "thumbnail_url": f"/thumbnails/{event_type}_clip.jpg",
                "clip_url": f"/clips/{event_type}_clip.mp4",
                "confidence": 0.9
            })
        
        return highlights
    
    def index_video_content(self, video_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create searchable index from video analysis
        Extracts semantic content for natural language queries
        """
        indexed_content = {
            "video_id": video_analysis.get("analysis_id"),
            "searchable_text": [],
            "tags": [],
            "events": []
        }
        
        # Extract searchable terms from events
        for event in video_analysis.get("detected_events", []):
            indexed_content["searchable_text"].append(event["description"])
            indexed_content["tags"].append(event["type"])
            indexed_content["events"].append({
                "type": event["type"],
                "timestamp": event["timestamp"],
                "confidence": event["confidence"]
            })
        
        # Add key moments
        for moment in video_analysis.get("key_moments", []):
            indexed_content["searchable_text"].append(moment["description"])
        
        return indexed_content


class SemanticSearchService:
    """
    Natural language search service
    Processes user queries and returns relevant results
    """
    
    def __init__(self):
        self.event_keywords = {
            "goal": ["goal", "scored", "finish", "shot on target"],
            "assist": ["assist", "pass", "through ball", "cross"],
            "dribble": ["dribble", "run", "beat defender", "skill move"],
            "defense": ["tackle", "interception", "clearance", "block"],
            "weakness": ["mistake", "error", "weakness", "poor", "lost possession"],
            "strength": ["excellent", "great", "strength", "good", "successful"]
        }
        self.twelve_labs = get_twelve_labs_analyzer()
        self.use_twelve_labs = self.twelve_labs is not None
    
    def parse_query(self, query: str) -> Dict[str, Any]:
        """
        Parse natural language query into structured search parameters
        """
        query_lower = query.lower()
        
        parsed = {
            "original_query": query,
            "event_types": [],
            "sentiment": "neutral",  # strength, weakness, neutral
            "player_mentioned": None,
            "time_context": None,
            "stats_query": False
        }
        
        # Detect event types
        for event_type, keywords in self.event_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                if event_type in ["weakness", "strength"]:
                    parsed["sentiment"] = event_type
                else:
                    parsed["event_types"].append(event_type)
        
        # Detect stats queries
        stats_keywords = ["how many", "count", "total", "average", "stats", "statistics"]
        if any(keyword in query_lower for keyword in stats_keywords):
            parsed["stats_query"] = True
        
        # Extract numbers (for stats queries)
        numbers = re.findall(r'\d+', query)
        if numbers:
            parsed["numeric_context"] = [int(n) for n in numbers]
        
        return parsed
    
    async def search_highlights(
        self, 
        db: Session, 
        query: str,
        player_id: Optional[str] = None,
        use_ai_search: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Search video highlights using natural language
        Uses Twelve Labs semantic search if available, falls back to database search
        """
        parsed_query = self.parse_query(query)
        
        # Try Twelve Labs semantic search first if enabled
        if self.use_twelve_labs and use_ai_search:
            try:
                # Get video IDs from database for the player
                video_ids = None
                if player_id:
                    highlights = db.query(VideoHighlightModel).filter(
                        VideoHighlightModel.player_id == player_id
                    ).all()
                    # Extract video IDs if they exist in metadata
                    video_ids = [h.video_url for h in highlights if h.video_url]
                
                # Perform semantic search using Twelve Labs
                twelve_labs_results = await self.twelve_labs.search_semantic(
                    query=query,
                    video_ids=video_ids,
                    page_limit=20
                )
                
                # Map Twelve Labs results to highlights in database
                scored_results = []
                for tl_result in twelve_labs_results:
                    # Find matching highlight in database
                    matching_highlights = db.query(VideoHighlightModel).filter(
                        VideoHighlightModel.video_url.contains(tl_result["video_id"])
                    ).all()
                    
                    for highlight in matching_highlights:
                        scored_results.append({
                            "highlight": highlight,
                            "relevance_score": tl_result["score"],
                            "matched_terms": [query],
                            "ai_matched": True
                        })
                
                if scored_results:
                    return scored_results
                    
            except Exception as e:
                print(f"Twelve Labs search error: {e}. Falling back to database search.")
        
        # Fallback to database search
        db_query = db.query(VideoHighlightModel)
        
        if player_id:
            db_query = db_query.filter(VideoHighlightModel.player_id == player_id)
        
        # Filter by sentiment/type
        if parsed_query["sentiment"] != "neutral":
            db_query = db_query.filter(VideoHighlightModel.type == parsed_query["sentiment"])
        
        # Get all potential matches (we'll score them later)
        results = db_query.all()
        
        # If we have specific search terms, filter by relevance
        if query.strip():
            # Filter results that match query terms in title, description, or tags
            query_lower = query.lower()
            filtered_results = []
            for highlight in results:
                # Check title and description
                text_match = (
                    query_lower in highlight.title.lower() or
                    query_lower in (highlight.description or "").lower()
                )
                
                # Check tags for event type matches
                tag_match = False
                if parsed_query["event_types"] and highlight.tags:
                    highlight_tags_lower = [tag.lower() for tag in highlight.tags]
                    # Check if any event type keywords match tags
                    for event_type in parsed_query["event_types"]:
                        # Map event types to related tags
                        event_keywords = self.event_keywords.get(event_type, [event_type])
                        for keyword in event_keywords:
                            if any(keyword in tag for tag in highlight_tags_lower):
                                tag_match = True
                                break
                
                # Include if there's any match
                if text_match or tag_match or not parsed_query["event_types"]:
                    filtered_results.append(highlight)
            
            results = filtered_results
        
        # Score and rank results
        scored_results = []
        for highlight in results:
            score = self._calculate_relevance_score(highlight, parsed_query)
            scored_results.append({
                "highlight": highlight,
                "relevance_score": score,
                "matched_terms": self._get_matched_terms(highlight, query),
                "ai_matched": False
            })
        
        # Sort by relevance
        scored_results.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return scored_results
    
    def _calculate_relevance_score(
        self, 
        highlight: VideoHighlightModel, 
        parsed_query: Dict[str, Any]
    ) -> float:
        """Calculate relevance score for a highlight"""
        score = 0.5  # Base score
        
        # Boost for matching event types
        if parsed_query["event_types"]:
            highlight_tags = highlight.tags or []
            for event_type in parsed_query["event_types"]:
                if event_type in [tag.lower() for tag in highlight_tags]:
                    score += 0.2
        
        # Boost for matching sentiment
        if parsed_query["sentiment"] != "neutral":
            if highlight.type == parsed_query["sentiment"]:
                score += 0.3
        
        # Boost for AI confidence
        if highlight.ai_insights:
            confidence = highlight.ai_insights.get("confidence", 0) / 100
            score += confidence * 0.2
        
        return min(score, 1.0)
    
    def _get_matched_terms(self, highlight: VideoHighlightModel, query: str) -> List[str]:
        """Extract matched terms from highlight"""
        matched = []
        query_words = query.lower().split()
        
        highlight_text = f"{highlight.title} {highlight.description}".lower()
        
        for word in query_words:
            if len(word) > 3 and word in highlight_text:
                matched.append(word)
        
        return matched


class PlayerReportService:
    """
    AI-powered player report generation
    Creates tactical evaluations and performance summaries
    """
    
    async def generate_report(
        self, 
        db: Session, 
        player_id: str,
        include_video_analysis: bool = True
    ) -> Dict[str, Any]:
        """
        Generate comprehensive AI report for a player
        """
        player = db.query(PlayerModel).filter(PlayerModel.id == player_id).first()
        if not player:
            raise ValueError(f"Player {player_id} not found")
        
        highlights = db.query(VideoHighlightModel).filter(
            VideoHighlightModel.player_id == player_id
        ).all()
        
        # Analyze player data
        report = {
            "player_id": player_id,
            "player_name": player.name,
            "report_id": f"report_{datetime.utcnow().timestamp()}",
            "generated_at": datetime.utcnow().isoformat(),
            "status": "completed",
            "summary": self._generate_summary(player, highlights),
            "tactical_analysis": self._generate_tactical_analysis(player, highlights),
            "strengths": self._identify_strengths(player, highlights),
            "weaknesses": self._identify_weaknesses(player, highlights),
            "statistics": self._compile_statistics(player, highlights),
            "recommendations": self._generate_recommendations(player, highlights),
            "video_highlights_count": len(highlights)
        }
        
        if include_video_analysis:
            report["key_moments"] = self._extract_key_moments(highlights)
        
        return report
    
    def _generate_summary(
        self, 
        player: PlayerModel, 
        highlights: List[VideoHighlightModel]
    ) -> str:
        """Generate executive summary"""
        position = player.position
        team = player.team
        age = player.age
        
        # Calculate performance indicators
        strength_count = sum(1 for h in highlights if h.type == "strength")
        weakness_count = sum(1 for h in highlights if h.type == "weakness")
        
        perf = player.recent_performance
        goals = perf.get("goals", 0)
        assists = perf.get("assists", 0)
        rating = perf.get("average_rating", 0)
        
        summary = f"{player.name} is a {age}-year-old {position} currently playing for {team}. "
        summary += f"Recent performance shows {goals} goals and {assists} assists with an average rating of {rating}. "
        
        if strength_count > weakness_count:
            summary += f"Analysis of {len(highlights)} video highlights reveals strong technical abilities, "
            summary += "particularly in offensive situations. "
        else:
            summary += "Video analysis indicates areas for development, especially in defensive positioning. "
        
        summary += "Overall, the player demonstrates consistent performance with clear tactical understanding."
        
        return summary
    
    def _generate_tactical_analysis(
        self, 
        player: PlayerModel, 
        highlights: List[VideoHighlightModel]
    ) -> Dict[str, Any]:
        """Generate tactical evaluation"""
        stats = player.stats
        
        return {
            "playing_style": self._determine_playing_style(player, highlights),
            "positional_awareness": {
                "rating": 7.5,
                "description": "Good understanding of spatial positioning and movement off the ball"
            },
            "decision_making": {
                "rating": 8.0,
                "description": "Makes intelligent choices under pressure, rarely loses possession unnecessarily"
            },
            "technical_ability": {
                "dribbling": stats.get("dribbling", 0),
                "passing": stats.get("passing", 0),
                "finishing": stats.get("finishing", 0)
            },
            "physical_attributes": {
                "speed": stats.get("speed", 0),
                "strength": stats.get("strength", 0)
            }
        }
    
    def _determine_playing_style(
        self, 
        player: PlayerModel, 
        highlights: List[VideoHighlightModel]
    ) -> str:
        """Determine player's playing style from stats and highlights"""
        stats = player.stats
        
        if stats.get("dribbling", 0) > 85 and stats.get("speed", 0) > 85:
            return "Dynamic, pace-oriented attacker with excellent dribbling skills"
        elif stats.get("passing", 0) > 85:
            return "Creative playmaker with vision and passing range"
        elif stats.get("finishing", 0) > 90:
            return "Clinical finisher with strong goal-scoring instinct"
        elif stats.get("defense", 0) > 80:
            return "Defensively solid with good positioning and tackling"
        else:
            return "Well-rounded player with balanced attributes"
    
    def _identify_strengths(
        self, 
        player: PlayerModel, 
        highlights: List[VideoHighlightModel]
    ) -> List[Dict[str, Any]]:
        """Identify player strengths from data"""
        strengths = []
        stats = player.stats
        
        # Analyze stats
        for stat_name, value in stats.items():
            if value >= 85:
                strengths.append({
                    "attribute": stat_name.capitalize(),
                    "rating": value,
                    "evidence": f"Consistently demonstrates high-level {stat_name} ability"
                })
        
        # Analyze highlights
        strength_highlights = [h for h in highlights if h.type == "strength"]
        if strength_highlights:
            # Group by tags
            tag_counts = {}
            for h in strength_highlights:
                for tag in h.tags or []:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
            
            # Add top tags as strengths
            for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:3]:
                strengths.append({
                    "attribute": tag,
                    "evidence": f"Demonstrated in {count} analyzed video clips",
                    "video_count": count
                })
        
        return strengths[:5]  # Top 5 strengths
    
    def _identify_weaknesses(
        self, 
        player: PlayerModel, 
        highlights: List[VideoHighlightModel]
    ) -> List[Dict[str, Any]]:
        """Identify areas for improvement"""
        weaknesses = []
        stats = player.stats
        
        # Analyze stats
        for stat_name, value in stats.items():
            if value < 60:
                weaknesses.append({
                    "attribute": stat_name.capitalize(),
                    "rating": value,
                    "recommendation": f"Focus on improving {stat_name} through targeted training"
                })
        
        # Analyze weakness highlights
        weakness_highlights = [h for h in highlights if h.type == "weakness"]
        if weakness_highlights:
            tag_counts = {}
            for h in weakness_highlights:
                for tag in h.tags or []:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
            
            for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:3]:
                weaknesses.append({
                    "attribute": tag,
                    "occurrences": count,
                    "recommendation": f"Address {tag.lower()} issues identified in match analysis"
                })
        
        return weaknesses[:5]  # Top 5 weaknesses
    
    def _compile_statistics(
        self, 
        player: PlayerModel, 
        highlights: List[VideoHighlightModel]
    ) -> Dict[str, Any]:
        """Compile comprehensive statistics"""
        perf = player.recent_performance
        
        return {
            "recent_performance": {
                "goals": perf.get("goals", 0),
                "assists": perf.get("assists", 0),
                "average_rating": perf.get("average_rating", 0),
                "minutes_played": perf.get("minutes_played", 0)
            },
            "video_analysis": {
                "total_highlights": len(highlights),
                "strengths_identified": sum(1 for h in highlights if h.type == "strength"),
                "weaknesses_identified": sum(1 for h in highlights if h.type == "weakness"),
                "average_ai_confidence": self._calculate_avg_confidence(highlights)
            },
            "attributes": player.stats
        }
    
    def _calculate_avg_confidence(self, highlights: List[VideoHighlightModel]) -> float:
        """Calculate average AI confidence across highlights"""
        if not highlights:
            return 0.0
        
        confidences = [
            h.ai_insights.get("confidence", 0) 
            for h in highlights 
            if h.ai_insights
        ]
        
        return sum(confidences) / len(confidences) if confidences else 0.0
    
    def _generate_recommendations(
        self, 
        player: PlayerModel, 
        highlights: List[VideoHighlightModel]
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        stats = player.stats
        
        # Based on stats
        if stats.get("defense", 0) < 60:
            recommendations.append(
                "Improve defensive positioning and tracking back to support the team"
            )
        
        if stats.get("passing", 0) > 85:
            recommendations.append(
                "Leverage exceptional passing ability to create more goal-scoring opportunities"
            )
        
        # Based on highlights
        weakness_count = sum(1 for h in highlights if h.type == "weakness")
        if weakness_count > len(highlights) * 0.3:
            recommendations.append(
                "Focus on consistency and reducing errors in high-pressure situations"
            )
        
        recommendations.append(
            "Continue developing technical skills through regular training and match experience"
        )
        
        return recommendations
    
    def _extract_key_moments(
        self, 
        highlights: List[VideoHighlightModel]
    ) -> List[Dict[str, Any]]:
        """Extract key moments from highlights"""
        key_moments = []
        
        for highlight in highlights[:10]:  # Top 10 highlights
            if highlight.ai_insights:
                moments = highlight.ai_insights.get("key_moments", [])
                for moment in moments:
                    key_moments.append({
                        "highlight_id": highlight.id,
                        "title": highlight.title,
                        "moment": moment,
                        "timestamp": highlight.timestamp
                    })
        
        return key_moments


class AnalyticsService:
    """
    Service for data aggregation and analytics
    Provides counting, statistics, and trend analysis
    """
    
    async def get_player_analytics(
        self, 
        db: Session, 
        player_id: str
    ) -> Dict[str, Any]:
        """Get comprehensive analytics for a player"""
        player = db.query(PlayerModel).filter(PlayerModel.id == player_id).first()
        if not player:
            raise ValueError(f"Player {player_id} not found")
        
        highlights = db.query(VideoHighlightModel).filter(
            VideoHighlightModel.player_id == player_id
        ).all()
        
        return {
            "player_id": player_id,
            "total_highlights": len(highlights),
            "highlights_by_type": self._count_by_type(highlights),
            "highlights_by_tag": self._count_by_tag(highlights),
            "performance_trends": self._analyze_trends(highlights),
            "ai_insights_summary": self._summarize_ai_insights(highlights),
            "recent_performance": player.recent_performance,
            "attribute_ratings": player.stats
        }
    
    def _count_by_type(self, highlights: List[VideoHighlightModel]) -> Dict[str, int]:
        """Count highlights by type"""
        counts = {"strength": 0, "weakness": 0, "neutral": 0}
        for h in highlights:
            counts[h.type] = counts.get(h.type, 0) + 1
        return counts
    
    def _count_by_tag(self, highlights: List[VideoHighlightModel]) -> Dict[str, int]:
        """Count highlights by tag"""
        tag_counts = {}
        for h in highlights:
            for tag in h.tags or []:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        return dict(sorted(tag_counts.items(), key=lambda x: x[1], reverse=True))
    
    def _analyze_trends(self, highlights: List[VideoHighlightModel]) -> Dict[str, Any]:
        """Analyze performance trends over time"""
        if not highlights:
            return {"trend": "insufficient_data"}
        
        # Sort by date
        sorted_highlights = sorted(highlights, key=lambda h: h.date)
        
        # Split into first half and second half
        mid = len(sorted_highlights) // 2
        first_half = sorted_highlights[:mid]
        second_half = sorted_highlights[mid:]
        
        first_half_strengths = sum(1 for h in first_half if h.type == "strength")
        second_half_strengths = sum(1 for h in second_half if h.type == "strength")
        
        if second_half_strengths > first_half_strengths:
            trend = "improving"
        elif second_half_strengths < first_half_strengths:
            trend = "declining"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "early_period_strengths": first_half_strengths,
            "recent_period_strengths": second_half_strengths,
            "total_analyzed_clips": len(highlights)
        }
    
    def _summarize_ai_insights(self, highlights: List[VideoHighlightModel]) -> Dict[str, Any]:
        """Summarize AI insights across all highlights"""
        if not highlights:
            return {}
        
        confidences = []
        all_key_moments = []
        
        for h in highlights:
            if h.ai_insights:
                confidences.append(h.ai_insights.get("confidence", 0))
                all_key_moments.extend(h.ai_insights.get("key_moments", []))
        
        return {
            "average_confidence": sum(confidences) / len(confidences) if confidences else 0,
            "total_key_moments_identified": len(all_key_moments),
            "insights_available": len([h for h in highlights if h.ai_insights])
        }
    
    async def get_global_statistics(self, db: Session) -> Dict[str, Any]:
        """Get global statistics across all players and highlights"""
        total_players = db.query(PlayerModel).count()
        total_highlights = db.query(VideoHighlightModel).count()
        
        all_highlights = db.query(VideoHighlightModel).all()
        
        return {
            "total_players": total_players,
            "total_highlights": total_highlights,
            "highlights_by_type": self._count_by_type(all_highlights),
            "most_common_tags": dict(list(self._count_by_tag(all_highlights).items())[:10]),
            "average_highlights_per_player": total_highlights / total_players if total_players > 0 else 0
        }


# Service instances
video_analysis_service = VideoAnalysisService()
semantic_search_service = SemanticSearchService()
player_report_service = PlayerReportService()
analytics_service = AnalyticsService()
