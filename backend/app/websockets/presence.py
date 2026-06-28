"""
Presence system for tracking user online status
"""

import asyncio
import time
from typing import Dict, Set
from enum import Enum


class PresenceStatus(str, Enum):
    ONLINE = "online"
    IDLE = "idle"
    DND = "dnd"  # Do Not Disturb
    OFFLINE = "offline"


class PresenceManager:
    def __init__(self):
        # Store user presence: {user_id: {"status": status, "last_seen": timestamp, "connections": count}}
        self.presence_data: Dict[int, Dict] = {}
        # Track WebSocket connections: {websocket: user_id}
        self.connection_map: Dict = {}
        # Time thresholds (in seconds)
        self.idle_timeout = 300  # 5 minutes of inactivity = idle
        self.offline_timeout = 600  # 10 minutes of disconnection = offline

    def set_presence(self, user_id: int, status: PresenceStatus, activity: str = None):
        """Set a user's presence status"""
        if user_id not in self.presence_data:
            self.presence_data[user_id] = {
                "status": status.value,
                "last_seen": time.time(),
                "connections": 0,
                "activity": activity
            }
        else:
            self.presence_data[user_id]["status"] = status.value
            self.presence_data[user_id]["last_seen"] = time.time()
            if activity is not None:
                self.presence_data[user_id]["activity"] = activity

    def user_connected(self, websocket, user_id: int):
        """Register a user connection"""
        self.connection_map[websocket] = user_id
        
        if user_id not in self.presence_data:
            self.presence_data[user_id] = {
                "status": PresenceStatus.ONLINE.value,
                "last_seen": time.time(),
                "connections": 0,
                "activity": None
            }
        
        self.presence_data[user_id]["connections"] += 1
        self.presence_data[user_id]["status"] = PresenceStatus.ONLINE.value
        self.presence_data[user_id]["last_seen"] = time.time()

    def user_disconnected(self, websocket):
        """Unregister a user connection"""
        if websocket in self.connection_map:
            user_id = self.connection_map[websocket]
            del self.connection_map[websocket]
            
            if user_id in self.presence_data:
                self.presence_data[user_id]["connections"] -= 1
                
                # If no more connections, mark as offline
                if self.presence_data[user_id]["connections"] <= 0:
                    self.presence_data[user_id]["connections"] = 0
                    self.presence_data[user_id]["status"] = PresenceStatus.OFFLINE.value

    def get_presence(self, user_id: int) -> Dict:
        """Get a user's presence information"""
        if user_id not in self.presence_data:
            return {
                "status": PresenceStatus.OFFLINE.value,
                "last_seen": None,
                "activity": None
            }
        
        user_data = self.presence_data[user_id].copy()
        
        # Update status based on last seen time if needed
        current_time = time.time()
        time_since_seen = current_time - user_data["last_seen"]
        
        if user_data["connections"] > 0:
            # User has active connections, so they're online or idle
            if time_since_seen > self.idle_timeout and user_data["status"] == PresenceStatus.ONLINE.value:
                user_data["status"] = PresenceStatus.IDLE.value
        else:
            # No active connections
            if time_since_seen > self.offline_timeout:
                user_data["status"] = PresenceStatus.OFFLINE.value
            elif time_since_seen > self.idle_timeout:
                user_data["status"] = PresenceStatus.IDLE.value
        
        return user_data

    def get_presences_for_guild(self, guild_id: int, user_ids: list) -> Dict[int, Dict]:
        """Get presence information for users in a specific guild"""
        presences = {}
        for user_id in user_ids:
            presences[user_id] = self.get_presence(user_id)
        return presences

    def heartbeat(self, user_id: int):
        """Update last seen time for a user (when they're active)"""
        if user_id in self.presence_data:
            self.presence_data[user_id]["last_seen"] = time.time()
            # If user was idle, bring them back to online
            if self.presence_data[user_id]["status"] == PresenceStatus.IDLE.value:
                self.presence_data[user_id]["status"] = PresenceStatus.ONLINE.value


# Global presence manager instance
presence_manager = PresenceManager()