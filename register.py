from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic

class Register(QMainWindow):
  def __init__(self):
    super(Register, self).__init__()
    uic.loadUi("register.ui", self)
