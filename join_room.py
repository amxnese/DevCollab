from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5 import QtWidgets
from room import Room
import sys
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
class Join_Room(QMainWindow):
  def __init__(self):
    super(Join_Room, self).__init__()
    uic.loadUi("join_room.ui", self)
    self.JoinButton.clicked.connect(self.join)
    self.label = ClickableLabel(self, self.centralwidget)
    self.label.setGeometry(QRect(10, 0, 47, 51)) 
    self.label.setAutoFillBackground(False)
    self.label.setText("")
    self.label.setPixmap(QtGui.QPixmap("arrow.svg"))
    self.label.setScaledContents(True)
    self.label.setObjectName("label")
    
  def join(self):
    code = self.room_id.text()
    if not code:
      QMessageBox.warning(self, 'Warning', "Please enter the room's id")
      return
    conn = sqlite3.connect('myDb.db')
    cur = conn.cursor()
    query = cur.execute(f"select project_id from Projects where project_id='{code}'")
    project_id = query.fetchone()
    if not project_id:
      QMessageBox.warning(self, 'Warning', "Room doesn't exist")
      # clear the input
      self.room_id.clear()
    else:
      # updating the current_project global variable
      globals.current_project = project_id[0]
      # showing the room's window
      self.room_ui = Room()
      self.room_ui.setupUi(self)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindowApp()
    main_window.show()
    sys.exit(app.exec_())
