from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtCore import Qt

import api_client
from session import session


class JoinRoomPage(QWidget):
    def __init__(self, navigate):
        super().__init__()
        self.navigate = navigate
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(120, 70, 120, 70)
        layout.setSpacing(14)
        layout.addStretch(1)
        logo = QLabel("DC")
        logo.setObjectName("logoMark")
        layout.addWidget(logo, 0, Qt.AlignmentFlag.AlignLeft)
        title = QLabel("Join a room")
        title.setObjectName("heroTitle")
        layout.addWidget(title)
        subtitle = QLabel("You need both the invite code and the room password. Guessing an old numeric ID won't get you in.")
        subtitle.setObjectName("subtitleLabel")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Invite code  •  XXXXX-XXXXX")
        layout.addWidget(self.code_input)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Room password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.returnPressed.connect(self.submit)
        layout.addWidget(self.password_input)
        self.join_button = QPushButton("Join room")
        self.join_button.clicked.connect(self.submit)
        layout.addWidget(self.join_button)
        back = QPushButton("← Back")
        back.setObjectName("secondaryButton")
        back.clicked.connect(lambda: self.navigate("home"))
        layout.addWidget(back)
        layout.addStretch(2)

    def submit(self):
        code, password = self.code_input.text().strip(), self.password_input.text()
        if not code or not password:
            QMessageBox.warning(self, "Missing info", "Enter the invite code and room password.")
            return
        self.join_button.setEnabled(False)
        try:
            room = api_client.join_room(code, password)
            session.set_room(room)
            self.code_input.clear(); self.password_input.clear()
            self.navigate("room")
        except api_client.ApiError as e:
            QMessageBox.warning(self, "Couldn't join room", str(e))
        finally:
            self.join_button.setEnabled(True)
