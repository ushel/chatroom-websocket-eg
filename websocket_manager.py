# websocket_manager.py
from fastapi import WebSocket
from typing import Dict, List, Tuple

class PrivateChatManager:
    def __init__(self):
        self.private_chats: Dict[Tuple[str, str], List[WebSocket]] = {}

    def _pair_key(self, u1: str, u2: str):
        return tuple(sorted([u1, u2]))

    async def connect(self, user1: str, user2: str, websocket: WebSocket):
        await websocket.accept()
        key = self._pair_key(user1, user2)
        if key not in self.private_chats:
            self.private_chats[key] = []
        self.private_chats[key].append(websocket)

    def disconnect(self, user1: str, user2: str, websocket: WebSocket):
        key = self._pair_key(user1, user2)
        if key in self.private_chats:
            if websocket in self.private_chats[key]:
                self.private_chats[key].remove(websocket)

            if not self.private_chats[key]:
                del self.private_chats[key]

    async def broadcast_private(self, user1: str, user2: str, message: str):
        key = self._pair_key(user1, user2)
        if key in self.private_chats:
            for ws in self.private_chats[key]:
                await ws.send_text(message)

manager = PrivateChatManager()
