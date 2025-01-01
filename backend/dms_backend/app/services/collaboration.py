from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import WebSocket
import json
import asyncio
import logging
from collections import defaultdict

class CollaborationManager:
    def __init__(self):
        self.active_connections: Dict[str, Dict[str, WebSocket]] = defaultdict(dict)
        self.document_locks: Dict[str, str] = {}  # document_id -> user_id
        self.user_cursors: Dict[str, Dict[str, Dict]] = defaultdict(dict)  # document_id -> {user_id -> cursor_position}
        self.document_changes: Dict[str, List[Dict]] = defaultdict(list)  # document_id -> [changes]

    async def connect(self, websocket: WebSocket, document_id: str, user_id: str):
        """Connect a user to a document's collaboration session"""
        await websocket.accept()
        self.active_connections[document_id][user_id] = websocket
        await self.broadcast_user_list(document_id)
        
        # Send current document state
        current_state = {
            'type': 'current_state',
            'locks': self.document_locks.get(document_id),
            'cursors': self.user_cursors[document_id],
            'changes': self.document_changes[document_id][-50:]  # Last 50 changes
        }
        await websocket.send_json(current_state)

    def disconnect(self, document_id: str, user_id: str):
        """Disconnect a user from a document's collaboration session"""
        if user_id in self.active_connections[document_id]:
            del self.active_connections[document_id][user_id]
        if document_id in self.document_locks and self.document_locks[document_id] == user_id:
            del self.document_locks[document_id]
        if user_id in self.user_cursors[document_id]:
            del self.user_cursors[document_id][user_id]
        asyncio.create_task(self.broadcast_user_list(document_id))

    async def broadcast_user_list(self, document_id: str):
        """Broadcast the list of active users to all connected clients"""
        if document_id in self.active_connections:
            message = {
                'type': 'users',
                'users': list(self.active_connections[document_id].keys())
            }
            await self.broadcast(document_id, message)

    async def broadcast(self, document_id: str, message: Dict):
        """Broadcast a message to all connected clients for a document"""
        if document_id in self.active_connections:
            for connection in self.active_connections[document_id].values():
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logging.error(f"Error broadcasting message: {str(e)}")

    async def handle_cursor_update(self, document_id: str, user_id: str, position: Dict):
        """Handle cursor position updates"""
        self.user_cursors[document_id][user_id] = {
            'position': position,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        message = {
            'type': 'cursor',
            'user_id': user_id,
            'position': position
        }
        await self.broadcast(document_id, message)

    async def handle_change(self, document_id: str, user_id: str, change: Dict):
        """Handle document changes"""
        if document_id in self.document_locks and self.document_locks[document_id] != user_id:
            return {
                'type': 'error',
                'message': 'Document is locked by another user'
            }

        # Record the change
        timestamp = datetime.utcnow().isoformat()
        change_record = {
            'user_id': user_id,
            'timestamp': timestamp,
            'change': change
        }
        self.document_changes[document_id].append(change_record)

        # Broadcast the change
        message = {
            'type': 'change',
            'change': change_record
        }
        await self.broadcast(document_id, message)
        return {'type': 'success'}

    async def acquire_lock(self, document_id: str, user_id: str) -> bool:
        """Attempt to acquire a document lock"""
        if document_id not in self.document_locks:
            self.document_locks[document_id] = user_id
            message = {
                'type': 'lock',
                'user_id': user_id,
                'locked': True
            }
            await self.broadcast(document_id, message)
            return True
        return False

    async def release_lock(self, document_id: str, user_id: str) -> bool:
        """Release a document lock"""
        if document_id in self.document_locks and self.document_locks[document_id] == user_id:
            del self.document_locks[document_id]
            message = {
                'type': 'lock',
                'user_id': user_id,
                'locked': False
            }
            await self.broadcast(document_id, message)
            return True
        return False

    def get_active_users(self, document_id: str) -> List[str]:
        """Get list of active users for a document"""
        return list(self.active_connections[document_id].keys())

    def get_user_cursor(self, document_id: str, user_id: str) -> Optional[Dict]:
        """Get a user's cursor position"""
        return self.user_cursors[document_id].get(user_id)

    def get_document_changes(self, document_id: str, limit: int = 50) -> List[Dict]:
        """Get recent changes for a document"""
        return self.document_changes[document_id][-limit:]

class CollaborationService:
    def __init__(self, db: Session):
        self.db = db
        self.manager = CollaborationManager()

    async def join_session(self, websocket: WebSocket, document_id: str, user_id: str):
        """Join a document collaboration session"""
        await self.manager.connect(websocket, document_id, user_id)

    def leave_session(self, document_id: str, user_id: str):
        """Leave a document collaboration session"""
        self.manager.disconnect(document_id, user_id)

    async def update_cursor(self, document_id: str, user_id: str, position: Dict):
        """Update cursor position"""
        await self.manager.handle_cursor_update(document_id, user_id, position)

    async def make_change(self, document_id: str, user_id: str, change: Dict):
        """Make a change to the document"""
        return await self.manager.handle_change(document_id, user_id, change)

    async def lock_document(self, document_id: str, user_id: str) -> bool:
        """Lock a document for exclusive editing"""
        return await self.manager.acquire_lock(document_id, user_id)

    async def unlock_document(self, document_id: str, user_id: str) -> bool:
        """Unlock a document"""
        return await self.manager.release_lock(document_id, user_id)

    def get_session_info(self, document_id: str) -> Dict:
        """Get information about a collaboration session"""
        return {
            'active_users': self.manager.get_active_users(document_id),
            'locked_by': self.manager.document_locks.get(document_id),
            'recent_changes': self.manager.get_document_changes(document_id)
        }
