from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QHBoxLayout
from PyQt6.QtCore import Qt

import api_client
from session import session


class CreateRoomPage(QWidget):
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
        title = QLabel("Create a private room")
        title.setObjectName("heroTitle")
        layout.addWidget(title)
        subtitle = QLabel("Give your team a room name and a password. The invite code is generated automatically.")
        subtitle.setObjectName("subtitleLabel")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Room name")
        layout.addWidget(self.name_input)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Room password (6+ characters)")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.returnPressed.connect(self.submit)
        layout.addWidget(self.password_input)
        self.create_button = QPushButton("Create private room")
        self.create_button.clicked.connect(self.submit)
        layout.addWidget(self.create_button)
        back = QPushButton("← Back")
        back.setObjectName("secondaryButton")
        back.clicked.connect(lambda: self.navigate("home"))
        layout.addWidget(back)
        layout.addStretch(2)

    def submit(self):
        name, password = self.name_input.text().strip(), self.password_input.text()
        if not name or not password:
            QMessageBox.warning(self, "Missing info", "Enter both a room name and a password.")
            return
        if len(password) < 6:
            QMessageBox.warning(self, "Weak password", "Use at least 6 characters.")
            return
        self.create_button.setEnabled(False)
        try:
            room = api_client.create_room(name, password)
            session.set_room(room)
            self.name_input.clear(); self.password_input.clear()
            QMessageBox.information(self, "Room created", f"Invite code: {room['invite_code']}\n\nShare both the invite code and room password with your collaborators.")
            self.navigate("room")
        except api_client.ApiError as e:
            QMessageBox.warning(self, "Couldn't create room", str(e))
        finally:
            self.create_button.setEnabled(True)
