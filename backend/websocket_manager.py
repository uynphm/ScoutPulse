"""
WebSocket Manager for Real-time Data Integration
Handles live updates for player data, video highlights, and analysis results
"""
from typing import Dict, List, Set
from fastapi import WebSocket
import json
import asyncio
from datetime import datetime


class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        # Active connections by type
        self.active_connections: Dict[str, Set[WebSocket]] = {
            "global": set(),  # Global updates
            "players": set(),  # Player-specific updates
            "highlights": set(),  # Highlight updates
            "analytics": set()  # Analytics updates
        }
        # Player-specific connections
        self.player_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, channel: str = "global"):
        """Accept new WebSocket connection"""
        await websocket.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = set()
        self.active_connections[channel].add(websocket)
    
    async def connect_player_channel(self, websocket: WebSocket, player_id: str):
        """Connect to player-specific channel"""
        await websocket.accept()
        if player_id not in self.player_connections:
            self.player_connections[player_id] = set()
        self.player_connections[player_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket, channel: str = "global"):
        """Remove WebSocket connection"""
        if channel in self.active_connections:
            self.active_connections[channel].discard(websocket)
    
    def disconnect_player_channel(self, websocket: WebSocket, player_id: str):
        """Disconnect from player-specific channel"""
        if player_id in self.player_connections:
            self.player_connections[player_id].discard(websocket)
    
    async def broadcast(self, message: dict, channel: str = "global"):
        """Broadcast message to all connections in a channel"""
        if channel not in self.active_connections:
            return
        
        disconnected = set()
        for connection in self.active_connections[channel]:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.add(connection)
        
        # Clean up disconnected clients
        for connection in disconnected:
            self.active_connections[channel].discard(connection)
    
    async def broadcast_to_player(self, message: dict, player_id: str):
        """Broadcast message to all connections watching a specific player"""
        if player_id not in self.player_connections:
            return
        
        disconnected = set()
        for connection in self.player_connections[player_id]:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.add(connection)
        
        # Clean up disconnected clients
        for connection in disconnected:
            self.player_connections[player_id].discard(connection)
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to specific connection"""
        try:
            await websocket.send_json(message)
        except Exception:
            pass
    
    def get_connection_count(self, channel: str = None) -> int:
        """Get number of active connections"""
        if channel:
            return len(self.active_connections.get(channel, set()))
        return sum(len(conns) for conns in self.active_connections.values())


class DataUpdateNotifier:
    """Handles notifications for data updates"""
    
    def __init__(self, connection_manager: ConnectionManager):
        self.manager = connection_manager
    
    async def notify_player_update(self, player_id: str, player_data: dict):
        """Notify clients about player data update"""
        message = {
            "type": "player_update",
            "timestamp": datetime.utcnow().isoformat(),
            "player_id": player_id,
            "data": player_data
        }
        await self.manager.broadcast_to_player(message, player_id)
        await self.manager.broadcast(message, "players")
    
    async def notify_highlight_added(self, highlight_data: dict):
        """Notify clients about new highlight"""
        message = {
            "type": "highlight_added",
            "timestamp": datetime.utcnow().isoformat(),
            "data": highlight_data
        }
        player_id = highlight_data.get("player_id")
        if player_id:
            await self.manager.broadcast_to_player(message, player_id)
        await self.manager.broadcast(message, "highlights")
    
    async def notify_analysis_complete(self, analysis_id: str, player_id: str, results: dict):
        """Notify clients about completed video analysis"""
        message = {
            "type": "analysis_complete",
            "timestamp": datetime.utcnow().isoformat(),
            "analysis_id": analysis_id,
            "player_id": player_id,
            "results": results
        }
        await self.manager.broadcast_to_player(message, player_id)
        await self.manager.broadcast(message, "analytics")
    
    async def notify_report_generated(self, report_id: str, player_id: str):
        """Notify clients about generated player report"""
        message = {
            "type": "report_generated",
            "timestamp": datetime.utcnow().isoformat(),
            "report_id": report_id,
            "player_id": player_id
        }
        await self.manager.broadcast_to_player(message, player_id)
    
    async def notify_stats_update(self, stats_data: dict):
        """Notify clients about global statistics update"""
        message = {
            "type": "stats_update",
            "timestamp": datetime.utcnow().isoformat(),
            "data": stats_data
        }
        await self.manager.broadcast(message, "analytics")


# Global instances
connection_manager = ConnectionManager()
data_notifier = DataUpdateNotifier(connection_manager)
