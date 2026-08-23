from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox,
    QFrame, QListWidget, QListWidgetItem, QTabWidget
)
from PyQt6.QtCore import Qt

import api_client
from session import session


class HomePage(QWidget):
    def __init__(self, navigate):
        super().__init__()
        self.navigate = navigate
        self._room_items = {}
        self._build_ui()

    def _logo(self):
        row = QHBoxLayout()
        mark = QLabel("DC")
        mark.setObjectName("logoMark")
        row.addWidget(mark, 0, Qt.AlignmentFlag.AlignVCenter)
        brand = QLabel("DevCollab")
        brand.setObjectName("brand")
        row.addWidget(brand, 0, Qt.AlignmentFlag.AlignVCenter)
        row.addStretch(1)
        return row

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(38, 30, 38, 30)
        outer.setSpacing(18)
        outer.addLayout(self._logo())

        top = QHBoxLayout()
        left = QVBoxLayout()
        self.hero = QLabel("Collaborate without the chaos.")
        self.hero.setObjectName("heroTitle")
        left.addWidget(self.hero)
        self.welcome_label = QLabel("")
        self.welcome_label.setObjectName("subtitleLabel")
        left.addWidget(self.welcome_label)
        top.addLayout(left, 1)

        self.logout_button = QPushButton("Log out")
        self.logout_button.setObjectName("secondaryButton")
        self.logout_button.clicked.connect(self.logout)
        top.addWidget(self.logout_button, 0, Qt.AlignmentFlag.AlignTop)
        outer.addLayout(top)

        actions = QHBoxLayout()
        self.create_button = QPushButton("＋  Create room")
        self.create_button.clicked.connect(lambda: self.navigate("create_room"))
        actions.addWidget(self.create_button)
        self.join_button = QPushButton("Join with invite code")
        self.join_button.setObjectName("secondaryButton")
        self.join_button.clicked.connect(lambda: self.navigate("join_room"))
        actions.addWidget(self.join_button)
        actions.addStretch(1)
        self.login_button = QPushButton("Log in")
        self.login_button.setObjectName("secondaryButton")
        self.login_button.clicked.connect(lambda: self.navigate("login"))
        actions.addWidget(self.login_button)
        self.register_button = QPushButton("Register")
        self.register_button.setObjectName("secondaryButton")
        self.register_button.clicked.connect(lambda: self.navigate("register"))
        actions.addWidget(self.register_button)
        outer.addLayout(actions)

        self.room_title_row = QHBoxLayout()
        title_row = self.room_title_row
        title = QLabel("Your rooms")
        title.setObjectName("titleLabel")
        title_row.addWidget(title)
        title_row.addStretch(1)
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setObjectName("secondaryButton")
        self.refresh_button.clicked.connect(self.refresh)
        title_row.addWidget(self.refresh_button)
        outer.addLayout(title_row)

        self.tabs = QTabWidget()
        self.tabs.setObjectName("homeRoomTabs")
        self.owned_list = QListWidget()
        self.owned_list.setSpacing(8)
        self.owned_list.setObjectName("roomList")
        self.joined_list = QListWidget()
        self.joined_list.setSpacing(8)
        self.joined_list.setObjectName("roomList")
        self.tabs.addTab(self.owned_list, "Your rooms")
        self.tabs.addTab(self.joined_list, "Joined rooms")
        outer.addWidget(self.tabs, 1)

    def refresh(self):
        logged_in = session.is_logged_in
        self.welcome_label.setText(
            f"Signed in as {session.username}. Your rooms stay attached to your account, so you won't need an invite code again."
            if logged_in else "Log in or create an account to start collaborating."
        )
        self.create_button.setEnabled(logged_in)
        self.join_button.setEnabled(logged_in)
        self.logout_button.setVisible(logged_in)
        self.refresh_button.setVisible(logged_in)
        self.login_button.setVisible(not logged_in)
        self.register_button.setVisible(not logged_in)
        self.tabs.setVisible(logged_in)
        self._set_room_section_visible(logged_in)
        self.owned_list.clear(); self.joined_list.clear(); self._room_items.clear()
        if not logged_in:
            return
        try:
            rooms = api_client.list_rooms()
        except api_client.ApiError as e:
            QMessageBox.warning(self, "Couldn't load rooms", str(e))
            return

        owned = [room for room in rooms if room.get("is_owner")]
        joined = [room for room in rooms if not room.get("is_owner")]
        self._populate(self.owned_list, owned, "You haven't created any rooms yet. Click + Create room to get started.")
        self._populate(self.joined_list, joined, "No joined rooms yet. A room owner can add you, or you can join with an invite code.")

    def _set_room_section_visible(self, visible: bool):
        # The room section is intentionally hidden before authentication so the
        # landing page does not show a confusing "Your rooms" heading.
        if hasattr(self, "room_title_row"):
            for i in range(self.room_title_row.count()):
                item = self.room_title_row.itemAt(i)
                widget = item.widget() if item else None
                if widget:
                    widget.setVisible(visible)

    def _populate(self, target_list, rooms, empty_text):
        if not rooms:
            empty = QListWidgetItem(empty_text)
            empty.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            target_list.addItem(empty)
            return
        for room in rooms:
            self._add_room(target_list, room)

    def _add_room(self, target_list, room):
        card = QFrame()
        card.setObjectName("card")
        layout = QHBoxLayout(card)
        layout.setContentsMargins(15, 12, 15, 12)
        info = QVBoxLayout()
        name = QLabel(room["name"])
        name.setObjectName("sectionTitle")
        info.addWidget(name)
        if room.get("is_owner"):
            detail = f"Owner · {room['member_count']} member(s) · Invite {room['invite_code']}"
        else:
            detail = f"Member · {room['member_count']} member(s)"
        code = QLabel(detail)
        code.setObjectName("muted")
        info.addWidget(code)
        layout.addLayout(info, 1)
        open_btn = QPushButton("Open")
        open_btn.clicked.connect(lambda _=False, r=room: self.open_room(r))
        layout.addWidget(open_btn)
        if room.get("is_owner"):
            delete_btn = QPushButton("Delete")
            delete_btn.setObjectName("dangerButton")
            delete_btn.clicked.connect(lambda _=False, r=room: self.delete_room(r))
            layout.addWidget(delete_btn)
        item = QListWidgetItem()
        item.setSizeHint(card.sizeHint())
        target_list.addItem(item)
        target_list.setItemWidget(item, card)
        self._room_items[room["id"]] = item

    def open_room(self, room):
        session.set_room(room)
        self.navigate("room")

    def delete_room(self, room):
        confirm = QMessageBox.question(self, "Delete room", f"Delete '{room['name']}' and all its tasks/comments?\n\nThis cannot be undone.")
        if confirm != QMessageBox.StandardButton.Yes:
            return
        try:
            api_client.delete_room(room["id"])
            self.refresh()
        except api_client.ApiError as e:
            QMessageBox.warning(self, "Couldn't delete room", str(e))

    def logout(self):
        session.logout()
        self.refresh()
