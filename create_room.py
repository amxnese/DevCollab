from PyQt5.QtWidgets import QMainWindow, QMessageBox
from room import Room
import sqlite3
from PyQt5 import uic, QtGui
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtCore import QRect
import globals

class ClickableLabel(QLabel):
    def __init__(self, login_ui, *args, **kwargs):
        super(ClickableLabel, self).__init__(*args, **kwargs)
        self.setCursor(Qt.PointingHandCursor)
        self.login_ui = login_ui

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
          from main import MainUI
          self.main_window = MainUI()
          self.main_window.show()
          self.login_ui.close()

class Create_Room(QMainWindow):
  def __init__(self):
    super(Create_Room, self).__init__()
    uic.loadUi("create_room.ui", self)
    self.CreateRoomButton.clicked.connect(self.submit)
    self.label = ClickableLabel(self, self.centralwidget)
    self.label.setGeometry(QRect(10, 0, 47, 51)) 
    self.label.setAutoFillBackground(False)
    self.label.setText("")
    self.label.setPixmap(QtGui.QPixmap("arrow.svg"))
    self.label.setScaledContents(True)
    self.label.setObjectName("label")
    
  def submit(self):
    # getting the name of the project
    name = self.room_name.text()
    # checking if the name is valid
    if not name:
      QMessageBox.warning(self, 'Warning', 'Please enter the name of the room')
    else:
      # inserting the project to the database
      conn = sqlite3.connect("myDb.db")
      cur = conn.cursor()
      cur.execute('insert into Projects (username, name) values (?,?)',(globals.current_user, name))
      # getting the id of the last inserted project
      project_id =  cur.lastrowid
      conn.commit()
      conn.close()
      globals.message = ['information', f"Your project's id is {project_id}"]
      globals.current_project = project_id
      # self.close()
      self.room_ui = Room()
      self.room_ui.setupUi(self)

