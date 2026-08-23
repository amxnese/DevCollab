from PyQt6.QtWidgets import QMainWindow, QStackedWidget

from pages.login_page import LoginPage
from pages.register_page import RegisterPage
from pages.home_page import HomePage
from pages.create_room_page import CreateRoomPage
from pages.join_room_page import JoinRoomPage
from pages.room_page import RoomPage
from session import session


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DevCollab")
        self.resize(1180, 760)
        self.setMinimumSize(900, 620)
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        self.pages = {
            "login": LoginPage(self.navigate),
            "register": RegisterPage(self.navigate),
            "home": HomePage(self.navigate),
            "create_room": CreateRoomPage(self.navigate),
            "join_room": JoinRoomPage(self.navigate),
            "room": RoomPage(self.navigate),
        }
        for page in self.pages.values(): self.stack.addWidget(page)
        self.navigate("home")

    def navigate(self, page_name: str):
        if page_name in ("create_room", "join_room", "room") and not session.is_logged_in:
            self.navigate("login"); return
        page = self.pages[page_name]
        if page_name == "home": page.refresh()
        elif page_name == "room": page.enter_room()
        self.stack.setCurrentWidget(page)

    def closeEvent(self, event):
        room_page = self.pages.get("room")
        if room_page: room_page._stop_websocket()
        event.accept()
