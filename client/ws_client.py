import json
import websocket
from PyQt6.QtCore import QThread, pyqtSignal

WS_BASE_URL = "ws://127.0.0.1:8000"


class RoomWebSocketClient(QThread):
    task_created = pyqtSignal(dict)
    task_updated = pyqtSignal(dict)
    task_deleted = pyqtSignal(int)
    comment_created = pyqtSignal(dict)
    comment_updated = pyqtSignal(dict)
    comment_deleted = pyqtSignal(dict)
    room_deleted = pyqtSignal()
    connection_error = pyqtSignal(str)

    def __init__(self, room_id: int, token: str, parent=None):
        super().__init__(parent)
        self.room_id = room_id
        self.token = token
        self._ws = None

    def run(self):
        url = f"{WS_BASE_URL}/ws/rooms/{self.room_id}?token={self.token}"
        try:
            self._ws = websocket.WebSocketApp(
                url,
                on_message=self._on_message,
                on_error=self._on_error,
            )
            self._ws.run_forever()
        except Exception as e:
            self.connection_error.emit(str(e))

    def _on_message(self, ws, message):
        try:
            payload = json.loads(message)
        except json.JSONDecodeError:
            return
        event, data = payload.get("event"), payload.get("data")
        if event == "task_created": self.task_created.emit(data)
        elif event == "task_updated": self.task_updated.emit(data)
        elif event == "task_deleted": self.task_deleted.emit(data.get("id"))
        elif event == "comment_created": self.comment_created.emit(data)
        elif event == "comment_updated": self.comment_updated.emit(data)
        elif event == "comment_deleted": self.comment_deleted.emit(data)
        elif event == "room_deleted": self.room_deleted.emit()

    def _on_error(self, ws, error):
        self.connection_error.emit(str(error))

    def stop(self):
        if self._ws:
            self._ws.close()
        self.wait(2000)
