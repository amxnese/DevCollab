from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5 import uic
from room import Room

class Join_Room(QMainWindow):
  def __init__(self):
    super(Join_Room, self).__init__()
    uic.loadUi("join_room.ui", self)
    self.JoinButton.clicked.connect(self.join)
    
  def join(self):
    if not self.room_id.text():
      QMessageBox.warning(self, 'Warning', "Please enter the room's id")
      return
    self.close()
    self.room_ui = Room()
    self.room_ui.show()
