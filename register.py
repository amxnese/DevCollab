from PyQt5.QtWidgets import QMainWindow, QMessageBox
from abstraction import Submitions
from PyQt5 import uic

# class Register(QMainWindow, Submitions):
class Register(QMainWindow):
  def __init__(self):
    super(Register, self).__init__()
    uic.loadUi("register.ui", self)
    self.register_button.clicked.connect(self.submit)

  def submit(self):
    if not self.username_reg.text():
      QMessageBox.warning(self, 'Warning', 'Please enter your username')
    elif not self.password_reg.text():
      QMessageBox.warning(self, 'Warning', 'Please enter your password')