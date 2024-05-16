from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5 import uic

class Create_Room(QMainWindow):
  def __init__(self):
    super(Create_Room, self).__init__()
    uic.loadUi("create_room.ui", self)
    self.CreateRoomButton.clicked.connect(self.submit)
    
  def submit(self):
    if not self.room_name.text():
      QMessageBox.warning(self, 'Warning', 'Please enter the name of the room')
