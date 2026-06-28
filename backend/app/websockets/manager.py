# backend/app/websockets/manager.py
import asyncio
from typing import Dict, List, Set
from fastapi import WebSocket
from datetime import datetime, timedelta

from .presence import presence_manager


class ConnectionManager:
    def __init__(self):
        # 核心結構：{ channel_id: [WebSocket1, WebSocket2, ...] }
        # 這樣我們才知道訊息要傳給哪個房間的人
        self.active_connections: Dict[int, List[WebSocket]] = {}
        # Track connection to user mapping: {websocket: user_id}
        self.connection_users: Dict[WebSocket, int] = {}
        # Track connection timestamps for rate limiting
        self.connection_timestamps: Dict[WebSocket, List[datetime]] = {}
        # Rate limiting: max 10 messages per 10 seconds per connection
        self.max_messages_per_interval = 10
        self.rate_limit_interval = 10  # seconds

    async def connect(self, websocket: WebSocket, channel_id: int, user_id: int):
        """ 當有使用者連線進來某個頻道時 """
        await websocket.accept()

        if channel_id not in self.active_connections:
            self.active_connections[channel_id] = []

        self.active_connections[channel_id].append(websocket)
        # Map connection to user
        self.connection_users[websocket] = user_id
        # Initialize rate limiting for this connection
        self.connection_timestamps[websocket] = []

        # Update presence
        presence_manager.user_connected(websocket, user_id)

        print(f"Client {user_id} joined channel {channel_id}")

    def disconnect(self, websocket: WebSocket, channel_id: int):
        """ 當使用者斷線時 (關閉視窗) """
        if channel_id in self.active_connections:
            if websocket in self.active_connections[channel_id]:
                self.active_connections[channel_id].remove(websocket)

                # Get user_id before removing from map
                user_id = self.connection_users.get(websocket)

                # Clean up rate limiting data
                if websocket in self.connection_timestamps:
                    del self.connection_timestamps[websocket]

                # Clean up user mapping
                if websocket in self.connection_users:
                    del self.connection_users[websocket]

                # Update presence
                presence_manager.user_disconnected(websocket)

                print(f"Client {user_id} left channel {channel_id}")

    def is_rate_limited(self, websocket: WebSocket) -> bool:
        """ Check if a connection is sending messages too rapidly """
        now = datetime.now()
        # Clean old timestamps (older than rate_limit_interval)
        self.connection_timestamps[websocket] = [
            ts for ts in self.connection_timestamps[websocket]
            if now - ts < timedelta(seconds=self.rate_limit_interval)
        ]

        # Check if too many messages in the interval
        if len(self.connection_timestamps[websocket]) >= self.max_messages_per_interval:
            return True

        # Add current timestamp
        self.connection_timestamps[websocket].append(now)
        return False

    def get_user_from_connection(self, websocket: WebSocket) -> int:
        """ Get user ID from WebSocket connection """
        return self.connection_users.get(websocket)

    async def broadcast(self, message: str, channel_id: int):
        """ 廣播訊息給同一頻道的所有人 """
        if channel_id in self.active_connections:
            # Create tasks for concurrent sending
            tasks = []
            for connection in self.active_connections[channel_id]:
                task = asyncio.create_task(self._send_to_connection(connection, message))
                tasks.append(task)

            # Wait for all sends to complete (with timeout)
            await asyncio.gather(*tasks, return_exceptions=True)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """ Send a message to a specific connection """
        try:
            await websocket.send_text(message)
        except Exception as e:
            print(f"Error sending personal message: {e}")
            # Clean up broken connection
            try:
                for channel_id, connections in self.active_connections.items():
                    if websocket in connections:
                        connections.remove(websocket)
                        user_id = self.connection_users.get(websocket)
                        if websocket in self.connection_timestamps:
                            del self.connection_timestamps[websocket]
                        if websocket in self.connection_users:
                            del self.connection_users[websocket]
                        presence_manager.user_disconnected(websocket)
                        print(f"Removed broken connection from channel {channel_id}")
                        break
            except:
                pass  # Ignore errors during cleanup

    async def _send_to_connection(self, connection: WebSocket, message: str):
        """ Helper method to send message to a single connection """
        try:
            await connection.send_text(message)
        except Exception as e:
            print(f"Error sending message to connection: {e}")
            # Optionally remove broken connections
            try:
                # Find which channel this connection belongs to and remove it
                for channel_id, connections in self.active_connections.items():
                    if connection in connections:
                        connections.remove(connection)
                        user_id = self.connection_users.get(connection)
                        if connection in self.connection_timestamps:
                            del self.connection_timestamps[connection]
                        if connection in self.connection_users:
                            del self.connection_users[connection]
                        presence_manager.user_disconnected(connection)
                        print(f"Removed broken connection from channel {channel_id}")
                        break
            except:
                pass  # Ignore errors during cleanup

# 建立一個全域的管理器實例
manager = ConnectionManager()