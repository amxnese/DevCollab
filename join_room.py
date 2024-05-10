from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic

class Join_Room(QMainWindow):
  def __init__(self):
    super(Join_Room, self).__init__()
    uic.loadUi("join_room.ui", self)
