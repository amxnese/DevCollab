from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
                              QMessageBox, QHBoxLayout)

import api_client
from session import session


class RegisterPage(QWidget):
    def __init__(self, navigate):
        super().__init__()
        self.navigate = navigate
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 60, 60, 60)
        layout.setSpacing(14)
        layout.addStretch(1)

        title = QLabel("Create your account")
        title.setObjectName("titleLabel")
        subtitle = QLabel("Username: 3-30 chars. Password: 6+ chars.")
        subtitle.setObjectName("subtitleLabel")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)

        self.confirm_input = QLineEdit()
        self.confirm_input.setPlaceholderText("Confirm password")
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_input.returnPressed.connect(self.submit)
        layout.addWidget(self.confirm_input)

        self.register_button = QPushButton("Create Account")
        self.register_button.clicked.connect(self.submit)
        layout.addWidget(self.register_button)

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
        self.confirm_input.clear()

    def submit(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        confirm = self.confirm_input.text()

        if len(username) < 3:
            QMessageBox.warning(self, "Invalid username", "Username must be at least 3 characters")
            return
        if len(password) < 6:
            QMessageBox.warning(self, "Weak password", "Password must be at least 6 characters")
            return
        if password != confirm:
            QMessageBox.warning(self, "Password mismatch", "Passwords don't match")
            return

        self.register_button.setEnabled(False)
        try:
            result = api_client.register(username, password)
            session.login(result["access_token"], result["username"])
            self.clear()
            QMessageBox.information(self, "Success", f"Account created for {result['username']}")
            self.navigate("home")
        except api_client.ApiError as e:
            QMessageBox.warning(self, "Registration failed", str(e))
        finally:
            self.register_button.setEnabled(True)
