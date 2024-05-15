from PyQt5.QtWidgets import QMainWindow
from abstraction import Submitions
from PyQt5 import uic

class Register(QMainWindow, Submitions):
  def __init__(self):
    super(Register, self).__init__()
    uic.loadUi("register.ui", self)

  def submit(self):
    pass
