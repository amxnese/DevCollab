from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QSizePolicy
from PyQt5 import uic
import sys
import os
from login import LoginUI
from join_room import Join_Room
from create_room import Create_Room
import globals

class MainUI(QMainWindow):
  def __init__(self):
    super(MainUI, self).__init__()
    uic.loadUi("home.ui", self)
    self.create_button.clicked.connect(self.create)
    self.join_button.clicked.connect(self.join)
    self.login_button.clicked.connect(self.login)
    self.register_button.clicked.connect(self.register)
    # checking if user is logged in
    if globals.current_user:
      self.welcome.setText(f'Welcome {globals.current_user}')
    self.show()

  def join(self):
    if not globals.current_user:
      QMessageBox.warning(self, 'Warning', 'You have to be logged in in order to join rooms')
    else:
      # closing the current window
      self.close()
      # opening the login window
      self.join_room = Join_Room()
      self.join_room.show()

  def create(self):
    # checking if logged in
    if not globals.current_user:
      QMessageBox.warning(self, 'Warning', 'You have be logged in in order to create rooms')
    else:
      # closing the current window
      self.close()
      # opening the login window
      self.create_room = Create_Room()
      self.create_room.show()

  def login(self):
    # checking if user already logged in
    if globals.current_user:
      QMessageBox.warning(self, 'Warning', f'You are already logged in as {globals.current_user}')
    else:
      # closing the current window
      self.close()
      # opening the login window
      self.login_ui = LoginUI()
      self.login_ui.show()

  def register(self):
    if globals.current_user:
      QMessageBox.warning(self, 'Warning', f'You are already logged in as {globals.current_user}')
    else:
      from register import Register
      # closing the current window
      self.close()
      # opening the login window
      self.register_ui = Register()
      self.register_ui.show()

# initialize the app
if __name__ == '__main__':
  app = QApplication(sys.argv)
  UIWindow = MainUI()
  app.exec_()