from PyQt5.QtWidgets import QMainWindow, QMessageBox
from room import Room
from PyQt5 import uic
import sqlite3
import globals

class Create_Room(QMainWindow):
  def __init__(self):
    super(Create_Room, self).__init__()
    uic.loadUi("create_room.ui", self)
    self.CreateRoomButton.clicked.connect(self.submit)
    
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

