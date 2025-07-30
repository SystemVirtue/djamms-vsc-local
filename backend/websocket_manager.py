from fastapi import WebSocket
from typing import Dict, Set, Any
import json
import asyncio

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {
            'player': set(),
            'signage': set(),
            'system': set(),
            'upload': set()
        }

    async def connect(self, websocket: WebSocket, client_type: str):
        await websocket.accept()
        if client_type not in self.active_connections:
            self.active_connections[client_type] = set()
        self.active_connections[client_type].add(websocket)

    def disconnect(self, websocket: WebSocket, client_type: str):
        self.active_connections[client_type].remove(websocket)

    async def broadcast_to_type(self, message: Any, client_type: str):
        if client_type in self.active_connections:
            dead_connections = set()
            for connection in self.active_connections[client_type]:
                try:
                    await connection.send_json(message)
                except:
                    dead_connections.add(connection)
            
            # Clean up dead connections
            for dead in dead_connections:
                self.active_connections[client_type].remove(dead)

    async def broadcast(self, message: Any):
        for client_type in self.active_connections:
            await self.broadcast_to_type(message, client_type)

class WebSocketEventHandler:
    def __init__(self):
        self.manager = ConnectionManager()
        self.event_handlers = {
            'player': self._handle_player_event,
            'signage': self._handle_signage_event,
            'system': self._handle_system_event
        }

    async def _handle_player_event(self, event: dict):
        event_type = event.get('type')
        if event_type == 'play':
            # Handle play event
            await self.manager.broadcast_to_type({
                'type': 'player_status',
                'status': 'playing',
                'track': event.get('track')
            }, 'player')
        # Add other player event handlers

    async def _handle_signage_event(self, event: dict):
        event_type = event.get('type')
        if event_type == 'content_update':
            # Handle content update
            await self.manager.broadcast_to_type({
                'type': 'signage_update',
                'content': event.get('content')
            }, 'signage')
        # Add other signage event handlers

    async def _handle_system_event(self, event: dict):
        event_type = event.get('type')
        if event_type == 'alert':
            # Handle system alert
            await self.manager.broadcast({
                'type': 'system_alert',
                'message': event.get('message'),
                'level': event.get('level')
            })
        # Add other system event handlers

    async def handle_event(self, event_type: str, event: dict):
        if event_type in self.event_handlers:
            await self.event_handlers[event_type](event)
