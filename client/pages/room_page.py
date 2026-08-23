from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QListWidget, QListWidgetItem, QMessageBox, QFrame, QSplitter
)
from PyQt6.QtCore import Qt

import api_client
from session import session
from ws_client import RoomWebSocketClient
from styles import COLOR_TEXT_DIM, COLOR_WOI, COLOR_COMPLETED


def _pretty_time(value: str) -> str:
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.strftime("%b %d · %H:%M")
    except Exception:
        return ""


class TaskWidget(QFrame):
    def __init__(self, task: dict):
        super().__init__()
        self.setObjectName("taskCard")
        self.task_id = task["id"]
        self.selected = False
        self._build_ui()
        self.update_from_task(task)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(8)
        head = QHBoxLayout()
        self.content_label = QLabel()
        self.content_label.setWordWrap(True)
        self.content_label.setStyleSheet("font-size: 16px; font-weight: 750;")
        head.addWidget(self.content_label, 1)
        self.status_label = QLabel()
        self.status_label.setObjectName("statusLabel")
        head.addWidget(self.status_label, 0, Qt.AlignmentFlag.AlignTop)
        layout.addLayout(head)
        self.meta_label = QLabel()
        self.meta_label.setObjectName("muted")
        layout.addWidget(self.meta_label)
        self.reactions_label = QLabel()
        self.reactions_label.setStyleSheet("font-size: 12px; color: #aeb6c7;")
        layout.addWidget(self.reactions_label)

    def set_selected(self, selected: bool):
        self.selected = selected
        self.setProperty("selected", "true" if selected else "false")
        self.style().unpolish(self); self.style().polish(self); self.update()

    def update_from_task(self, task: dict):
        self.task = task
        self.content_label.setText(task["content"])
        self.meta_label.setText(f"Created by {task['username']}  ·  {_pretty_time(task['created_at'])}")
        self.reactions_label.setText(f"♥ {task['likes']}     ♡ {task['dislikes']}")
        status = task.get("status")
        statusby = task.get("statusby")
        if status == "woi":
            self.status_label.setText(f"● {statusby} is working on it")
            self.status_label.setStyleSheet(f"color: {COLOR_WOI}; font-weight: 700;")
        elif status == "completed":
            self.status_label.setText(f"✓ Done by {statusby}")
            self.status_label.setStyleSheet(f"color: {COLOR_COMPLETED}; font-weight: 700;")
        else:
            self.status_label.setText("")


class CommentWidget(QFrame):
    def __init__(self, comment, current_username, callbacks):
        super().__init__()
        self.setObjectName("commentCard")
        self.comment_id = comment["id"]
        self.callbacks = callbacks
        self.current_username = current_username
        self._build_ui()
        self.update_from_comment(comment)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)
        head = QHBoxLayout()
        self.meta = QLabel(); self.meta.setObjectName("muted")
        head.addWidget(self.meta, 1)
        self.delete_button = QPushButton("Delete")
        self.delete_button.setObjectName("dangerButton")
        self.delete_button.setFixedWidth(65)
        self.delete_button.clicked.connect(lambda: self.callbacks["delete"](self.comment_id))
        head.addWidget(self.delete_button)
        layout.addLayout(head)
        self.content = QLabel(); self.content.setWordWrap(True)
        layout.addWidget(self.content)
        buttons = QHBoxLayout()
        self.like_button = QPushButton("♥ 0")
        self.like_button.setObjectName("likeButton")
        self.like_button.clicked.connect(lambda: self.callbacks["like"](self.comment_id))
        buttons.addWidget(self.like_button)
        self.dislike_button = QPushButton("♡ 0")
        self.dislike_button.setObjectName("dislikeButton")
        self.dislike_button.clicked.connect(lambda: self.callbacks["dislike"](self.comment_id))
        buttons.addWidget(self.dislike_button)
        buttons.addStretch(1)
        layout.addLayout(buttons)

    def update_from_comment(self, comment):
        self.comment = comment
        self.meta.setText(f"{comment['username']}  ·  {_pretty_time(comment['created_at'])}")
        self.content.setText(comment["content"])
        self.like_button.setText(f"♥ {comment['likes']}")
        self.dislike_button.setText(f"♡ {comment['dislikes']}")
        self.delete_button.setVisible(comment["username"] == self.current_username)


class RoomPage(QWidget):
    def __init__(self, navigate):
        super().__init__()
        self.navigate = navigate
        self.ws_client = None
        self.task_items = {}
        self.comment_items = {}
        self.current_comments_task_id = None
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(26, 22, 26, 22)
        outer.setSpacing(14)

        header = QHBoxLayout()
        brand = QLabel("DC"); brand.setObjectName("logoMark")
        header.addWidget(brand)
        room_title_box = QVBoxLayout()
        self.room_name_label = QLabel("Room")
        self.room_name_label.setObjectName("titleLabel")
        room_title_box.addWidget(self.room_name_label)
        self.room_info_label = QLabel(""); self.room_info_label.setObjectName("subtitleLabel")
        room_title_box.addWidget(self.room_info_label)
        header.addLayout(room_title_box, 1)
        self.delete_room_button = QPushButton("Delete room")
        self.delete_room_button.setObjectName("dangerButton")
        self.delete_room_button.clicked.connect(self.delete_room)
        header.addWidget(self.delete_room_button)
        self.exit_button = QPushButton("Exit room")
        self.exit_button.setObjectName("secondaryButton")
        self.exit_button.setToolTip("Return to your rooms without leaving this room")
        self.exit_button.clicked.connect(self.exit_room)
        header.addWidget(self.exit_button)

        self.leave_button = QPushButton("Leave")
        self.leave_button.setObjectName("secondaryButton")
        self.leave_button.setToolTip("Leave this room and remove yourself from its members")
        self.leave_button.clicked.connect(self.leave_room)
        header.addWidget(self.leave_button)
        outer.addLayout(header)

        invite_row = QHBoxLayout()
        self.invite_label = QLabel(""); self.invite_label.setObjectName("muted")
        invite_row.addWidget(self.invite_label, 1)
        self.copy_button = QPushButton("Copy invite code")
        self.copy_button.setObjectName("secondaryButton")
        self.copy_button.clicked.connect(self.copy_invite)
        invite_row.addWidget(self.copy_button)
        outer.addLayout(invite_row)

        self.member_admin_card = QFrame(); self.member_admin_card.setObjectName("card")
        member_admin_layout = QVBoxLayout(self.member_admin_card)
        member_admin_layout.setContentsMargins(14, 12, 14, 12)
        member_title = QLabel("Add people to this room"); member_title.setObjectName("sectionTitle")
        member_admin_layout.addWidget(member_title)
        member_search_row = QHBoxLayout()
        self.member_search_input = QLineEdit()
        self.member_search_input.setPlaceholderText("Search users by username...")
        self.member_search_input.returnPressed.connect(self.search_users)
        member_search_row.addWidget(self.member_search_input, 1)
        self.member_search_button = QPushButton("Search")
        self.member_search_button.setObjectName("secondaryButton")
        self.member_search_button.clicked.connect(self.search_users)
        member_search_row.addWidget(self.member_search_button)
        member_admin_layout.addLayout(member_search_row)
        self.member_results = QListWidget(); self.member_results.setMaximumHeight(125); self.member_results.setSpacing(3)
        member_admin_layout.addWidget(self.member_results)
        outer.addWidget(self.member_admin_card)

        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("What needs doing? Add a clear task or decision...")
        self.task_input.returnPressed.connect(self.add_task)
        add_row = QHBoxLayout()
        add_row.addWidget(self.task_input, 1)
        add_btn = QPushButton("＋ Add task")
        add_btn.clicked.connect(self.add_task)
        add_row.addWidget(add_btn)
        outer.addLayout(add_row)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.tasks_list = QListWidget()
        self.tasks_list.setSpacing(6)
        self.tasks_list.currentItemChanged.connect(self._selection_changed)
        splitter.addWidget(self.tasks_list)

        detail = QFrame(); detail.setObjectName("card")
        d = QVBoxLayout(detail); d.setContentsMargins(18, 16, 18, 16); d.setSpacing(10)
        self.selected_title = QLabel("Select a task"); self.selected_title.setObjectName("sectionTitle")
        d.addWidget(self.selected_title)
        self.selected_meta = QLabel("Pick a task to see discussion and actions."); self.selected_meta.setObjectName("muted")
        self.selected_meta.setWordWrap(True); d.addWidget(self.selected_meta)

        actions = QHBoxLayout()
        for label, object_name, slot in [
            ("♥ Like", "likeButton", self.like_selected),
            ("♡ Dislike", "dislikeButton", self.dislike_selected),
            ("Working", "statusButton", lambda: self.set_status_selected("woi")),
            ("Done", "statusButton", lambda: self.set_status_selected("completed")),
            ("Delete task", "dangerButton", self.remove_selected),
        ]:
            btn = QPushButton(label); btn.setObjectName(object_name); btn.clicked.connect(slot); actions.addWidget(btn)
            if label == "Delete task": self.remove_button = btn
        d.addLayout(actions)

        comments_title = QLabel("Discussion"); comments_title.setObjectName("sectionTitle")
        d.addWidget(comments_title)
        self.comments_list = QListWidget(); self.comments_list.setSpacing(6); d.addWidget(self.comments_list, 1)
        comment_row = QHBoxLayout()
        self.comment_input = QLineEdit(); self.comment_input.setPlaceholderText("Add your opinion...")
        self.comment_input.returnPressed.connect(self.add_comment)
        comment_row.addWidget(self.comment_input, 1)
        comment_btn = QPushButton("Comment"); comment_btn.clicked.connect(self.add_comment); comment_row.addWidget(comment_btn)
        d.addLayout(comment_row)
        splitter.addWidget(detail)
        splitter.setSizes([540, 460])
        outer.addWidget(splitter, 1)

    def enter_room(self):
        self.room_name_label.setText(session.current_room_name or "Room")
        self.room_info_label.setText("Private collaborative workspace")
        self.invite_label.setText(f"Invite code:  {session.current_room_invite_code or 'hidden'}")
        self.delete_room_button.setVisible(session.current_room_is_owner)
        self.leave_button.setVisible(True)
        self.member_admin_card.setVisible(session.current_room_is_owner)
        self.member_results.clear()
        self.member_search_input.clear()
        self.current_comments_task_id = None
        self.load_tasks()
        self._start_websocket()

    def copy_invite(self):
        if session.current_room_invite_code:
            QApplication.clipboard().setText(session.current_room_invite_code)
            QMessageBox.information(self, "Copied", "Invite code copied to clipboard.")

    def _start_websocket(self):
        self._stop_websocket()
        self.ws_client = RoomWebSocketClient(session.current_room_id, session.token)
        self.ws_client.task_created.connect(self._on_task_created)
        self.ws_client.task_updated.connect(self._on_task_updated)
        self.ws_client.task_deleted.connect(self._on_task_deleted)
        self.ws_client.comment_created.connect(self._on_comment_created)
        self.ws_client.comment_updated.connect(self._on_comment_updated)
        self.ws_client.comment_deleted.connect(self._on_comment_deleted)
        self.ws_client.room_deleted.connect(self._on_room_deleted)
        self.ws_client.start()

    def _stop_websocket(self):
        if self.ws_client:
            self.ws_client.stop(); self.ws_client = None

    def load_tasks(self):
        self.tasks_list.clear(); self.task_items.clear()
        try:
            tasks = api_client.list_tasks(session.current_room_id)
        except api_client.ApiError as e:
            QMessageBox.warning(self, "Couldn't load tasks", str(e)); return
        for task in tasks: self._add_task_item(task)

    def _add_task_item(self, task):
        widget = TaskWidget(task)
        item = QListWidgetItem()
        item.setSizeHint(widget.sizeHint())
        self.tasks_list.addItem(item); self.tasks_list.setItemWidget(item, widget)
        self.task_items[task["id"]] = item

    def _selection_changed(self, current, previous):
        if previous:
            old = self.tasks_list.itemWidget(previous)
            if old: old.set_selected(False)
        if not current:
            return
        widget = self.tasks_list.itemWidget(current)
        if not widget: return
        widget.set_selected(True)
        self.selected_title.setText(widget.task["content"])
        self.selected_meta.setText(f"Created by {widget.task['username']} · {_pretty_time(widget.task['created_at'])}")
        self.remove_button.setEnabled(widget.task["username"] == session.username or session.current_room_is_owner)
        self.load_comments(widget.task_id)

    def _selected_task_id(self):
        item = self.tasks_list.currentItem()
        if not item: return None
        return self.tasks_list.itemWidget(item).task_id

    def add_task(self):
        content = self.task_input.text().strip()
        if not content: return
        try:
            api_client.add_task(session.current_room_id, content)
            self.task_input.clear()
        except api_client.ApiError as e: QMessageBox.warning(self, "Couldn't add task", str(e))

    def like_selected(self): self._task_action(api_client.like_task)
    def dislike_selected(self): self._task_action(api_client.dislike_task)

    def _task_action(self, action):
        task_id = self._selected_task_id()
        if task_id is None:
            QMessageBox.information(self, "No task selected", "Select a task first."); return
        try: action(task_id)
        except api_client.ApiError as e: QMessageBox.warning(self, "Action failed", str(e))

    def set_status_selected(self, new_status):
        task_id = self._selected_task_id()
        if task_id is None: return
        try: api_client.set_status(task_id, new_status)
        except api_client.ApiError as e: QMessageBox.warning(self, "Action failed", str(e))

    def remove_selected(self):
        task_id = self._selected_task_id()
        if task_id is None: return
        item = self.tasks_list.currentItem(); task = self.tasks_list.itemWidget(item).task
        if task["username"] != session.username and not session.current_room_is_owner:
            QMessageBox.warning(self, "Not allowed", "Only the task creator or a room admin can delete this task."); return
        confirm = QMessageBox.question(self, "Delete task", "Delete this task and its discussion?")
        if confirm != QMessageBox.StandardButton.Yes: return
        try: api_client.delete_task(task_id)
        except api_client.ApiError as e: QMessageBox.warning(self, "Action failed", str(e))

    # ----- comments -----
    def load_comments(self, task_id):
        self.current_comments_task_id = task_id
        self.comments_list.clear(); self.comment_items.clear()
        try: comments = api_client.list_comments(task_id)
        except api_client.ApiError as e:
            QMessageBox.warning(self, "Couldn't load discussion", str(e)); return
        for comment in comments: self._add_comment_item(comment)

    def _add_comment_item(self, comment):
        widget = CommentWidget(comment, session.username, {
            "like": self.like_comment, "dislike": self.dislike_comment, "delete": self.delete_comment,
        })
        item = QListWidgetItem(); item.setSizeHint(widget.sizeHint())
        self.comments_list.addItem(item); self.comments_list.setItemWidget(item, widget)
        self.comment_items[comment["id"]] = item

    def add_comment(self):
        if self.current_comments_task_id is None: return
        content = self.comment_input.text().strip()
        if not content: return
        try:
            api_client.add_comment(self.current_comments_task_id, content)
            self.comment_input.clear()
        except api_client.ApiError as e: QMessageBox.warning(self, "Couldn't comment", str(e))

    def like_comment(self, comment_id):
        try: api_client.like_comment(comment_id)
        except api_client.ApiError as e: QMessageBox.warning(self, "Action failed", str(e))

    def dislike_comment(self, comment_id):
        try: api_client.dislike_comment(comment_id)
        except api_client.ApiError as e: QMessageBox.warning(self, "Action failed", str(e))

    def delete_comment(self, comment_id):
        confirm = QMessageBox.question(self, "Delete comment", "Delete this comment?")
        if confirm != QMessageBox.StandardButton.Yes: return
        try: api_client.delete_comment(comment_id)
        except api_client.ApiError as e: QMessageBox.warning(self, "Action failed", str(e))

    # ----- member management -----
    def search_users(self):
        if not session.current_room_is_owner:
            return
        query = self.member_search_input.text().strip()
        if len(query) < 2:
            QMessageBox.information(self, "Search", "Enter at least 2 characters.")
            return
        try:
            users = api_client.search_users(query)
            members = api_client.list_room_members(session.current_room_id)
            member_ids = {u["id"] for u in members}
        except api_client.ApiError as e:
            QMessageBox.warning(self, "Couldn't search users", str(e))
            return
        self.member_results.clear()
        available = [u for u in users if u["id"] not in member_ids]
        if not available:
            self.member_results.addItem("No available users found.")
            return
        for user in available:
            row = QFrame(); row.setObjectName("card")
            layout = QHBoxLayout(row); layout.setContentsMargins(8, 4, 8, 4)
            label = QLabel(f"@{user['username']}"); label.setObjectName("sectionTitle")
            layout.addWidget(label, 1)
            add_btn = QPushButton("Add")
            add_btn.clicked.connect(lambda _=False, uid=user["id"], name=user["username"]: self.add_member(uid, name))
            layout.addWidget(add_btn)
            item = QListWidgetItem(); item.setSizeHint(row.sizeHint())
            self.member_results.addItem(item); self.member_results.setItemWidget(item, row)

    def add_member(self, user_id, username):
        try:
            api_client.add_room_member(session.current_room_id, user_id)
            QMessageBox.information(self, "Member added", f"{username} can now open this room directly from Joined rooms.")
            self.search_users()
        except api_client.ApiError as e:
            QMessageBox.warning(self, "Couldn't add member", str(e))

    # ----- websocket -----
    def _on_task_created(self, task):
        if task["id"] not in self.task_items: self._add_task_item(task)

    def _on_task_updated(self, task):
        item = self.task_items.get(task["id"])
        if item:
            widget = self.tasks_list.itemWidget(item); widget.update_from_task(task); item.setSizeHint(widget.sizeHint())
            if item is self.tasks_list.currentItem():
                self.remove_button.setEnabled(task["username"] == session.username or session.current_room_is_owner)

    def _on_task_deleted(self, task_id):
        item = self.task_items.pop(task_id, None)
        if item:
            row = self.tasks_list.row(item); self.tasks_list.takeItem(row)
        if self.current_comments_task_id == task_id:
            self.comments_list.clear(); self.comment_items.clear(); self.current_comments_task_id = None
            self.selected_title.setText("Select a task")

    def _on_comment_created(self, comment):
        if comment["task_id"] == self.current_comments_task_id and comment["id"] not in self.comment_items:
            self._add_comment_item(comment)

    def _on_comment_updated(self, comment):
        item = self.comment_items.get(comment["id"])
        if item:
            widget = self.comments_list.itemWidget(item); widget.update_from_comment(comment); item.setSizeHint(widget.sizeHint())

    def _on_comment_deleted(self, data):
        item = self.comment_items.pop(data["id"], None)
        if item:
            row = self.comments_list.row(item); self.comments_list.takeItem(row)

    def _on_room_deleted(self):
        self._stop_websocket()
        session.current_room_id = None
        QMessageBox.information(self, "Room deleted", "The room creator deleted this room.")
        self.navigate("home")

    def delete_room(self):
        # UI currently exposes this only after server-side owner verification; the server is authoritative.
        confirm = QMessageBox.question(self, "Delete room", "Delete this entire room, including every task and comment?\n\nThis cannot be undone.")
        if confirm != QMessageBox.StandardButton.Yes: return
        try:
            api_client.delete_room(session.current_room_id)
            self._stop_websocket(); session.current_room_id = None; self.navigate("home")
        except api_client.ApiError as e: QMessageBox.warning(self, "Couldn't delete room", str(e))

    def exit_room(self):
        """Close the room view while keeping the user's membership intact."""
        self._stop_websocket()
        session.current_room_id = None
        self.navigate("home")

    def leave_room(self):
        if session.current_room_is_owner:
            message = "Leave this room? Ownership will be transferred to the longest-standing remaining member."
        else:
            message = "Leave this room? It will remain in your account history only if you are re-added later."
        confirm = QMessageBox.question(self, "Leave room", message)
        if confirm != QMessageBox.StandardButton.Yes: return
        try:
            api_client.leave_room(session.current_room_id)
            self._stop_websocket(); session.current_room_id = None; self.navigate("home")
        except api_client.ApiError as e: QMessageBox.warning(self, "Couldn't leave room", str(e))
