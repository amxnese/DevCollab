from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QLabel, QListWidgetItem, QMessageBox
from PyQt5 import QtCore, QtGui, QtWidgets
import sqlite3
from PyQt5 import QtGui
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtCore import QRect
import globals
from PyQt5.QtCore import QTimer

class ClickableLabel(QLabel):
    def __init__(self, room, *args, **kwargs):
        super(ClickableLabel, self).__init__(*args, **kwargs)
        self.setCursor(Qt.PointingHandCursor)
        self.room = room

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            from join_room import Join_Room
            self.join_room = Join_Room()
            self.join_room.show()
            self.room.close()

class TaskWidget(QWidget):
    def __init__(self, task_name, likes=0, dislikes=0, task_id=None):
        super().__init__()
        # collecting infos
        self.task_name = task_name
        self.likes = likes
        self.dislikes = dislikes
        self.task_id = task_id
        
        # creating a horizontal layout
        self.layout = QHBoxLayout(self)
        
        # creating objects that will be put in the task
        self.task_label = QLabel(self.task_name)
        self.likes_label = QLabel(f'Likes: {self.likes}')
        self.dislikes_label = QLabel(f'Dislikes: {self.dislikes}')
        
        # adding objects to the horizontal layout and now we have a task widget
        self.layout.addWidget(self.task_label)
        self.layout.addWidget(self.likes_label)
        self.layout.addWidget(self.dislikes_label)

    def add_like(self):
        self.likes += 1
        self.likes_label.setText(f'Likes: {self.likes}')

    def take_like(self):
        self.likes -= 1
        self.likes_label.setText(f'Likes: {self.likes}')

    def add_dislike(self):
        self.dislikes += 1
        self.dislikes_label.setText(f'Dislikes: {self.dislikes}')

    def take_dislike(self):
        self.dislikes -= 1
        self.dislikes_label.setText(f'Dislikes: {self.dislikes}')
    
    def get_id(self):
        return self.task_id

class Room(QWidget):
    def setupUi(self, Main_Window):
        Main_Window.setObjectName("Main_Window")
        Main_Window.setWindowModality(QtCore.Qt.NonModal)
        Main_Window.setEnabled(True)
        Main_Window.resize(800, 600)
        Main_Window.setSizeIncrement(QtCore.QSize(500, 500))
        Main_Window.setMouseTracking(False)
        Main_Window.setTabletTracking(False)
        Main_Window.setContextMenuPolicy(QtCore.Qt.PreventContextMenu)
        Main_Window.setAcceptDrops(False)
        Main_Window.setLayoutDirection(QtCore.Qt.LeftToRight)
        Main_Window.setAutoFillBackground(False)
        Main_Window.setStyleSheet("#tasks_widget{\n"
"    background-color: rgb(203, 203, 203);\n"
"    border-radius: 5px;\n"
"    border-style: solid;\n"
"    border-width: 1px;\n"
"    padding: 3px;\n"
"    color: black\n"
"}\n"
"#room_name_label{\n"
"    \n"
"}\n"
"#tasks_widget::item:hover {\n"
"    background-color: linear-gradient(135deg, rgb(171, 171, 171), rgb(100, 100, 100));\n"
"    color: white;\n"
"}\n"
"#like_button:hover{\n"
"    cursor: pointer;\n"
"}\n"
"QMainWindow{\n"
"    background-color: #6495ED;\n"
"}\n"
"#like_button{\n"
"    background-color: rgb(103, 144, 255);\n"
"}\n"
"QPushButton{\n"
"color: black;\n"
"    border-radius: 10px;\n"
"    padding: 10px;\n"
"    border: none;\n"
"}\n"
"#like_button {\n"
"   background: qlineargradient(\n"
"        spread:pad, x1:0, y1:0, x2:1, y2:1, \n"
"        stop:0 rgba(66, 103, 178, 255), \n"
"        stop:1 rgba(0, 51, 153, 255)\n"
"    );\n"
"}\n"
"\n"
"#dislike_button{\n"
"    background: qlineargradient(\n"
"        spread:pad, x1:0, y1:0, x2:1, y2:1, \n"
"        stop:0 rgba(255, 140, 0, 255), \n"
"        stop:1 rgba(255, 69, 0, 255)\n"
"    );\n"
"}\n"
"#add_task_button{\n"
"    background: qlineargradient(\n"
"        spread:pad, x1:0, y1:0, x2:1, y2:1, \n"
"        stop:0 rgba(245, 245, 245, 255), \n"
"        stop:1 rgba(220, 220, 220, 255)\n"
"    );\n"
"}\n"
"#remove_button{\n"
"    background: qlineargradient(\n"
"        spread:pad, x1:0, y1:0, x2:1, y2:1, \n"
"        stop:0 rgba(220, 20, 60, 255), \n"
"        stop:1 rgba(178, 34, 34, 255)\n"
"    );\n"
"}\n"
"#woi_button{\n"
"    background: qlineargradient(\n"
"        spread:pad, x1:0, y1:0, x2:1, y2:1, \n"
"        stop:0 rgba(255, 223, 0, 255), \n"
"        stop:1 rgba(255, 200, 0, 255)\n"
"    );\n"
"}\n"
"#completed_button{\n"
"    background: qlineargradient(\n"
"        spread:pad, x1:0, y1:0, x2:1, y2:1, \n"
"        stop:0 rgba(34, 139, 34, 255), \n"
"        stop:1 rgba(0, 255, 0, 255)\n"
"    );\n"
"}\n"
"\n"
"")
        Main_Window.setDocumentMode(False)
        Main_Window.setTabShape(QtWidgets.QTabWidget.Rounded)
        Main_Window.setDockNestingEnabled(False)

        self.centralwidget = QtWidgets.QWidget(Main_Window)
        self.centralwidget.setObjectName("centralwidget")

        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.gridLayout.setContentsMargins(10, 10, 10, 10)
        self.gridLayout.setObjectName("gridLayout")

        self.room_name_label = QtWidgets.QLabel(self.centralwidget)
        self.room_name_label.setMinimumSize(QtCore.QSize(0, 60))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.room_name_label.setFont(font)
        self.room_name_label.setAlignment(QtCore.Qt.AlignCenter)
        self.room_name_label.setObjectName("room_name_label")
        self.gridLayout.addWidget(self.room_name_label, 0, 0, 1, 6)

        self.task_input = QtWidgets.QLineEdit(self.centralwidget)
        self.task_input.setMinimumSize(QtCore.QSize(0, 50))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.task_input.setFont(font)
        self.task_input.setCursorMoveStyle(QtCore.Qt.LogicalMoveStyle)
        self.task_input.setObjectName("task_input")
        self.gridLayout.addWidget(self.task_input, 1, 0, 1, 6)

        self.add_task_button = QtWidgets.QPushButton(self.centralwidget)
        self.add_task_button.setMinimumSize(QtCore.QSize(0, 27))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.add_task_button.setFont(font)
        self.add_task_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.add_task_button.setObjectName("add_task_button")
        self.gridLayout.addWidget(self.add_task_button, 2, 0, 1, 1)

        self.like_button = QtWidgets.QPushButton(self.centralwidget)
        self.like_button.setMinimumSize(QtCore.QSize(0, 27))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.like_button.setFont(font)
        self.like_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.like_button.setObjectName("like_button")
        self.gridLayout.addWidget(self.like_button, 2, 1, 1, 1)

        self.dislike_button = QtWidgets.QPushButton(self.centralwidget)
        self.dislike_button.setMinimumSize(QtCore.QSize(0, 27))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.dislike_button.setFont(font)
        self.dislike_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.dislike_button.setObjectName("dislike_button")
        self.gridLayout.addWidget(self.dislike_button, 2, 2, 1, 1)

        self.woi_button = QtWidgets.QPushButton(self.centralwidget)
        self.woi_button.setMinimumSize(QtCore.QSize(0, 27))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.woi_button.setFont(font)
        self.woi_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.woi_button.setObjectName("woi_button")
        self.gridLayout.addWidget(self.woi_button, 2, 3, 1, 1)

        self.completed_button = QtWidgets.QPushButton(self.centralwidget)
        self.completed_button.setMinimumSize(QtCore.QSize(0, 27))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.completed_button.setFont(font)
        self.completed_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.completed_button.setObjectName("completed_button")
        self.gridLayout.addWidget(self.completed_button, 2, 4, 1, 1)

        self.remove_button = QtWidgets.QPushButton(self.centralwidget)
        self.remove_button.setMinimumSize(QtCore.QSize(0, 27))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.remove_button.setFont(font)
        self.remove_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.remove_button.setObjectName("remove_button")
        self.gridLayout.addWidget(self.remove_button, 2, 5, 1, 1)

        self.tasks_widget = QtWidgets.QListWidget(self.centralwidget)
        self.tasks_widget.setBaseSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(False)
        font.setWeight(50)
        self.tasks_widget.setFont(font)
        self.tasks_widget.setObjectName("tasks_widget")
        self.gridLayout.addWidget(self.tasks_widget, 3, 0, 1, 6)

        Main_Window.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(Main_Window)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 22))
        self.menubar.setObjectName("menubar")
        Main_Window.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(Main_Window)
        self.statusbar.setObjectName("statusbar")
        Main_Window.setStatusBar(self.statusbar)

        self.retranslateUi(Main_Window)
        QtCore.QMetaObject.connectSlotsByName(Main_Window)

        self.label = ClickableLabel(Main_Window, self.centralwidget)
        self.label.setGeometry(QRect(10, 0, 47, 51)) 
        self.label.setAutoFillBackground(False)
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap("arrow.svg"))
        self.label.setScaledContents(True)
        self.label.setObjectName("label")

        ''' LOGIC '''

        self.add_task_button.clicked.connect(self.add_task)
        self.remove_button.clicked.connect(self.remove_task)
        self.woi_button.clicked.connect(self.working_on_it)
        self.completed_button.clicked.connect(self.completed)
        self.like_button.clicked.connect(self.like_selected_task)
        self.dislike_button.clicked.connect(self.dislike_selected_task)
        # Checking for messages from other windows
        if globals.message:
            # Delaying the message so it won't appear before the window
            QTimer.singleShot(50, self.show_message)

        try:
            # fetching tasks related to the room
            conn = sqlite3.connect('myDb.db')
            cur = conn.cursor()
            tasks = cur.execute(f'select * from tasks where project_id={globals.current_project}').fetchall()
            for task in tasks:
                task_id = task[0]
                likes = task[3]
                dislikes = task[4]
                status = task[5]
                task_content = task[6]
                task_widget = TaskWidget(task_content, likes, dislikes, task_id)
                list_item = QListWidgetItem(self.tasks_widget)
                list_item.setSizeHint(task_widget.sizeHint())
                self.tasks_widget.addItem(list_item)
                self.tasks_widget.setItemWidget(list_item, task_widget)
                if status:
                    if status == 'woi':
                        list_item.setBackground(QtGui.QColor(253, 255, 93))
                    elif status == 'completed':
                        list_item.setBackground(QtGui.QColor(0, 255, 0))

            # changing the room name label
            project_name = cur.execute(f'select name from Projects where project_id={globals.current_project}').fetchone()[0]
            self.room_name_label.setText(f"{project_name}")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred: {e}")
        finally:
            conn.close()
        
    def show_message(self):
        if globals.message and globals.message[0] == 'information':
            QMessageBox.information(self, 'information', globals.message[1])
            globals.message = None

    # event for the add task button
    def add_task(self, likes=0, dislikes=0, task_id=None):
        try:
            # getting the user's input
            task = self.task_input.text()
            if not task:
                return

            # adding the task to the database
            conn = sqlite3.connect('myDb.db')
            cur = conn.cursor()
            cur.execute('''
                insert into Tasks (project_id, username, content, likes, dislikes) values (?, ?, ?, ?, ?)
            ''', (globals.current_project, globals.current_user, task, likes, dislikes))
            # getting the last added task
            task_id = cur.lastrowid
            conn.commit()

            # creating an instance of the class TaskWidget
            task_widget = TaskWidget(task, int(likes), dislikes, task_id) # horizontal layout
            # creating an item to put it on the listWidget
            list_item = QListWidgetItem(self.tasks_widget)
            # giving the item a proper size
            list_item.setSizeHint(task_widget.sizeHint())
            # adding the task to the list widget
            self.tasks_widget.addItem(list_item)
            # setting the task_widget as the widget to be displayed within list_item
            self.tasks_widget.setItemWidget(list_item, task_widget)
            # clearing the input
            self.task_input.clear()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred: {e}")
        finally:
            conn.close()
        
    def like_selected_task(self):
        selected = self.tasks_widget.currentItem()
        # checking if the user selected any task
        if selected:
            try:
                conn = sqlite3.connect('myDb.db')
                cur = conn.cursor()

                # getting the task's id
                task_widget = self.tasks_widget.itemWidget(selected)
                task_id = task_widget.get_id()

                # checking if the user already liked that task
                interacted = cur.execute('''
                select type from interactions where username=? and task_id=?
                ''', (globals.current_user, task_id)).fetchone()
                # case where user hasn't interacted with the task
                if not interacted:
                    cur.execute('''
                        insert into Interactions (task_id, username, type) values(?, ?, ?)
                    ''', (task_id, globals.current_user, 'like'))

                    # incrementing likes
                    task_widget.add_like()

                    # updating likes on database
                    cur.execute('update tasks set likes=likes+1 where task_id=?', (task_id,))
                elif interacted[0] == 'dislike':
                    # changing the type of interaction in database
                    cur.execute(f"update interactions set type='like' where task_id={task_id} and username='{globals.current_user}'")
                    # incrementing likes and decrementing dislikes
                    task_widget.add_like()
                    task_widget.take_dislike()
                # case where already liked, removing the like
                elif interacted[0] == 'like':
                    # deleting interaction from database
                    cur.execute(f"delete from interactions where task_id={task_id} and username='{globals.current_user}'")
                    # decrementing the task's likes
                    cur.execute(f"update tasks set likes=likes-1 where task_id=?", (task_id,))
                    # decrementing likes
                    task_widget.take_like()

                conn.commit()
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", f"An error occurred: {e}")
            finally:
                conn.close()

    def dislike_selected_task(self):
        selected = self.tasks_widget.currentItem()
        # checking if the user selected any task
        if selected:
            try:
                conn = sqlite3.connect('myDb.db')
                cur = conn.cursor()

                # getting the task's id
                task_widget = self.tasks_widget.itemWidget(selected)
                task_id = task_widget.get_id()

                # checking if the user already disliked that task
                interacted = cur.execute('''
                select type from interactions where username=? and task_id=?
                ''', (globals.current_user, task_id)).fetchone()
                # case where user hasn't interacted with the task
                if not interacted:
                    cur.execute('''
                        insert into Interactions (task_id, username, type) values(?, ?, ?)
                    ''', (task_id, globals.current_user, 'dislike'))

                    # incrementing dislikes
                    task_widget.add_dislike()

                    # updating dislikes on database
                    cur.execute('update tasks set dislikes=dislikes+1 where task_id=?', (task_id,))
                elif interacted[0] == 'like':
                    # changing the type of interaction in database
                    cur.execute(f"update interactions set type='dislike' where task_id={task_id} and username='{globals.current_user}'")
                    # incrementing dislikes and decrementing likes
                    task_widget.add_dislike()
                    task_widget.take_like()
                # case where already disliked, removing the dislike
                elif interacted[0] == 'dislike':
                    # deleting interaction from database
                    cur.execute(f"delete from interactions where task_id={task_id} and username='{globals.current_user}'")
                    # decrementing the task's dislikes
                    cur.execute(f"update tasks set dislikes=dislikes-1 where task_id=?", (task_id,))
                    # decrementing dislikes
                    task_widget.take_dislike()

                conn.commit()
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", f"An error occurred: {e}")
            finally:
                conn.close()

    # event for remove button
    def remove_task(self):
        selected = self.tasks_widget.currentItem()
        if selected:
            try:
                task_widget = self.tasks_widget.itemWidget(selected)
                task_id = task_widget.get_id()

                # checking if the user can delete the task
                conn = sqlite3.connect('myDb.db')
                cur = conn.cursor()
                owner = cur.execute('select username from tasks where task_id=?', (task_id,)).fetchone()[0]
                admin = cur.execute('select username from projects where project_id=?', (globals.current_project,)).fetchone()[0]
                if owner == globals.current_user or admin == globals.current_user:
                    # removing task
                    row = self.tasks_widget.row(selected)
                    self.tasks_widget.takeItem(row)
                    # removing task from database
                    cur.execute('delete from tasks where task_id=?', (task_id,))
                    conn.commit()
                else:
                    QMessageBox.warning(self, 'Invalid', 'only the owner of the task and the admin can delete this task')
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", f"An error occurred: {e}")
            finally:
                conn.close()

    def working_on_it(self):
        selected = self.tasks_widget.currentItem()
        if selected:
            try:
                task_id = self.tasks_widget.itemWidget(selected).get_id()
                # updating database
                conn = sqlite3.connect('myDb.db')
                cur = conn.cursor()
                status = cur.execute('select status from tasks where task_id=?', (task_id,)).fetchone()[0]
                status_by =  cur.execute('select statusby from tasks where task_id=?', (task_id,)).fetchone()[0]
                if status == 'woi':
                    if status_by == globals.current_user:
                        selected.setBackground(QtGui.QColor(203, 203, 203))
                        cur.execute(f'UPDATE tasks SET statusby = ? where task_id=?', (None, task_id))
                        cur.execute('UPDATE tasks SET status = ? WHERE task_id = ?', (None, task_id))
                    else:
                        QMessageBox.warning(self, 'Invalid', f'this task is already being worked on by {status_by}')
                elif status == 'completed':
                    if status_by == globals.current_user:
                        selected.setBackground(QtGui.QColor(253, 255, 93))
                        cur.execute('update tasks set status=? where task_id=?', ('woi', task_id))
                    else:
                        QMessageBox.warning(self, 'Invalid', f'task has been already completed by {status_by}')
                else:
                    selected.setBackground(QtGui.QColor(253, 255, 93))
                    cur.execute('update tasks set status=? where task_id=?', ('woi', task_id))
                    cur.execute('update tasks set statusby=? where task_id=?', (globals.current_user, task_id))
                conn.commit()
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", f"An error occurred: {e}")
            finally:
                conn.close()

    def completed(self):
        selected = self.tasks_widget.currentItem()
        if selected:
            try:
                # updating database
                conn = sqlite3.connect('myDb.db')
                cur = conn.cursor()
                task_id = self.tasks_widget.itemWidget(selected).get_id()
                status = cur.execute('select status from tasks where task_id=?', (task_id,)).fetchone()[0]
                status_by =  cur.execute('select statusby from tasks where task_id=?', (task_id,)).fetchone()[0]
                # case where selected task is already completed
                if status == 'completed':
                    # case where task is completed by the logged in user
                    if status_by == globals.current_user:
                        selected.setBackground(QtGui.QColor(203, 203, 203))
                        cur.execute(f'UPDATE tasks SET statusby = ? where task_id=?', (None, task_id))
                        cur.execute('UPDATE tasks SET status = ? WHERE task_id = ?', (None, task_id))
                    else:
                        QMessageBox.warning(self, 'Invalid', f'task has been already completed by {status_by}')
                elif status == 'woi':
                    if status_by == globals.current_user:
                        selected.setBackground(QtGui.QColor(0, 255, 0))
                        cur.execute('update tasks set status=? where task_id=?', ('completed', task_id))
                        cur.execute('update tasks set statusby=? where task_id=?', (globals.current_user, task_id))
                    else:
                        QMessageBox.warning(self, 'Invalid', f'task is already being worked on by {status_by}')
                else:
                    selected.setBackground(QtGui.QColor(0, 255, 0))
                    cur.execute('update tasks set status=? where task_id=?', ('completed', task_id))
                    cur.execute('update tasks set statusby=? where task_id=?', (globals.current_user, task_id))
                conn.commit()
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", f"An error occurred: {e}")
            finally:
                conn.close()

    def retranslateUi(self, Main_Window):
        _translate = QtCore.QCoreApplication.translate
        Main_Window.setWindowTitle(_translate("Main_Window", "MainWindow"))
        self.dislike_button.setText(_translate("Main_Window", "Dislike"))
        self.room_name_label.setText(_translate("Main_Window", "username\'s room"))
        self.woi_button.setText(_translate("Main_Window", "Working on it"))
        self.like_button.setText(_translate("Main_Window", "Like"))
        self.add_task_button.setText(_translate("Main_Window", "Add Task"))
        self.task_input.setPlaceholderText(_translate("Main_Window", "Add a Task Here..."))
        self.remove_button.setText(_translate("Main_Window", "Remove"))
        self.completed_button.setText(_translate("Main_Window", "Completed"))

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Main_Window = QtWidgets.QMainWindow()
    ui = Room()
    ui.setupUi(Main_Window)
    Main_Window.show()
    sys.exit(app.exec_())
