from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic

class LoginUI(QMainWindow):
  def __init__(self):
    super(LoginUI, self).__init__()
    uic.loadUi("login.ui", self)
