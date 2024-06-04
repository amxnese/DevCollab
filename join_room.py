from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5 import QtWidgets
from PyQt5 import uic
from room import Room
import sys
import sqlite3
import globals

class Join_Room(QMainWindow):
  def __init__(self):
    super(Join_Room, self).__init__()
    uic.loadUi("join_room.ui", self)
    self.JoinButton.clicked.connect(self.join)
    
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
