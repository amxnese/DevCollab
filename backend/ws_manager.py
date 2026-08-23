import json
from typing import Dict, List
from fastapi import WebSocket


class RoomConnectionManager:
    def __init__(self):
        self.rooms: Dict[int, List[WebSocket]] = {}

    async def connect(self, room_id: int, websocket: WebSocket):
        await websocket.accept()
        self.rooms.setdefault(room_id, []).append(websocket)

    def disconnect(self, room_id: int, websocket: WebSocket):
        if room_id in self.rooms and websocket in self.rooms[room_id]:
            self.rooms[room_id].remove(websocket)
            if not self.rooms[room_id]:
                del self.rooms[room_id]

    async def broadcast(self, room_id: int, event_type: str, payload: dict):
        if room_id not in self.rooms:
            return
        message = json.dumps({"event": event_type, "data": payload})
        dead = []
        for conn in list(self.rooms[room_id]):
            try:
                await conn.send_text(message)
            except Exception:
                dead.append(conn)
        for conn in dead:
            self.disconnect(room_id, conn)


manager = RoomConnectionManager()
