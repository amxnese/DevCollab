from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic

class Create_Room(QMainWindow):
  def __init__(self):
    super(Create_Room, self).__init__()
    uic.loadUi("create_room.ui", self)
