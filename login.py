from PyQt5.QtWidgets import QMainWindow
from abstraction import Submitions
from PyQt5 import uic

class LoginUI(QMainWindow, Submitions):
  def __init__(self):
    super(LoginUI, self).__init__()
    uic.loadUi("login.ui", self)
  
  def submit(self):
    pass