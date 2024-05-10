from PyQt5.QtWidgets import QMainWindow, QLabel, QApplication, QPushButton, QLineEdit, QListWidget, QGridLayout, QVBoxLayout
from PyQt5 import uic
import sys
import os
from login import LoginUI
from register import Register
from join_room import Join_Room
from create_room import Create_Room

class UI(QMainWindow):
  def __init__(self):
    super(UI, self).__init__()
    uic.loadUi("home.ui", self)
    self.create_button.clicked.connect(self.create)
    self.join_button.clicked.connect(self.join)
    self.login_button.clicked.connect(self.login)
    self.register_button.clicked.connect(self.register)
    self.show()

  def join(self):
    # closing the current window
    self.close()
    # opening the login window
    self.join_room = Join_Room()
    self.join_room.show()

  def create(self):
    # closing the current window
    self.close()
    # opening the login window
    self.create_room = Create_Room()
    self.create_room.show()

  def login(self):
    # closing the current window
    self.close()
    # opening the login window
    self.login_ui = LoginUI()
    self.login_ui.show()

  def register(self):
    # closing the current window
    self.close()
    # opening the login window
    self.register_ui = Register()
    self.register_ui.show()

# initialize the app
app = QApplication(sys.argv)
UIWindow = UI()
app.exec_()