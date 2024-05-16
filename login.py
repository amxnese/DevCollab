from PyQt5.QtWidgets import QMainWindow, QMessageBox
from abstraction import Submitions
from PyQt5 import uic

# class LoginUI(QMainWindow, Submitions):
class LoginUI(QMainWindow):
  def __init__(self):
    super(LoginUI, self).__init__()
    uic.loadUi("login.ui", self)
    self.login_button.clicked.connect(self.submit)
    
  def submit(self):
    if not self.username_login.text():
      QMessageBox.warning(self, 'Warning', 'Please enter your username')
    elif not self.password_login.text():
      QMessageBox.warning(self, 'Warning', 'Please enter your password')
    
