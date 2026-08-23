from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
                              QMessageBox, QHBoxLayout)
from PyQt6.QtCore import Qt

import api_client
from session import session


class LoginPage(QWidget):
    def __init__(self, navigate):
        super().__init__()
        self.navigate = navigate
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 60, 60, 60)
        layout.setSpacing(14)
        layout.addStretch(1)

        title = QLabel("Welcome back")
        title.setObjectName("titleLabel")
        subtitle = QLabel("Log in to continue to your rooms")
        subtitle.setObjectName("subtitleLabel")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.returnPressed.connect(self.submit)
        layout.addWidget(self.password_input)

        self.login_button = QPushButton("Log In")
        self.login_button.clicked.connect(self.submit)
        layout.addWidget(self.login_button)

        back_row = QHBoxLayout()
        back_button = QPushButton("← Back")
        back_button.setObjectName("secondaryButton")
        back_button.clicked.connect(lambda: self.navigate("home"))
        back_row.addWidget(back_button)
        back_row.addStretch(1)
        layout.addLayout(back_row)

        layout.addStretch(2)

    def clear(self):
        self.username_input.clear()
        self.password_input.clear()

    def submit(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        if not username:
            QMessageBox.warning(self, "Missing info", "Please enter your username")
            return
        if not password:
            QMessageBox.warning(self, "Missing info", "Please enter your password")
            return

        self.login_button.setEnabled(False)
        try:
            result = api_client.login(username, password)
            session.login(result["access_token"], result["username"])
            self.clear()
            self.navigate("home")
        except api_client.ApiError as e:
            QMessageBox.warning(self, "Login failed", str(e))
        finally:
            self.login_button.setEnabled(True)
