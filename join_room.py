from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5 import uic
from room import Room
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
      project_id = project_id[0]
      globals.current_project = project_id
      self.close()
      self.room_ui = Room()
      self.room_ui.show()
