from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QSizePolicy
import sys
import os
from login import LoginUI
from join_room import Join_Room
from create_room import Create_Room
from PyQt5 import uic, QtGui
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMouseEvent, QPixmap
from PyQt5.QtCore import QRect
import globals

class ClickableLabel(QLabel):
    def __init__(self, parent,  *args, **kwargs):
        super(ClickableLabel, self).__init__(*args, **kwargs)
        self.setCursor(Qt.PointingHandCursor)
        self.parent_window = parent

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
          globals.current_user = None
          QMessageBox.information(self, 'Information', 'You have been succesfully logged out')
          self.parent_window.show()
          self.close()
class MainUI(QMainWindow):
  def __init__(self):
    super(MainUI, self).__init__()
    uic.loadUi("home.ui", self)
    self.create_button.clicked.connect(self.create)
    self.join_button.clicked.connect(self.join)
    self.login_button.clicked.connect(self.login)
    self.register_button.clicked.connect(self.register)
    self.setMaximumSize(690, 375)
    self.setMinimumSize(690, 375)
    # checking if user is logged in
    if globals.current_user:
      self.welcome.setText(f'Welcome {globals.current_user}')
      # logout icon
      self.label = ClickableLabel(self, self.centralwidget)
      self.label.setGeometry(QRect(10, 10, 55, 55))
      self.label.setAutoFillBackground(False)
      self.label.setText("")
      self.label.setPixmap(QtGui.QPixmap("logout1.png"))
      self.label.setScaledContents(True)
      self.label.setObjectName("label")

    self.show()

  def join(self):
    if not globals.current_user:
      QMessageBox.warning(self, 'Warning', 'You have to be logged in in order to join rooms')
    else:
      # opening the login window
      self.join_room = Join_Room()
      self.join_room.show()
      # closing the current window
      self.close()

  def create(self):
    # checking if logged in
    if not globals.current_user:
      QMessageBox.warning(self, 'Warning', 'You have be logged in in order to create rooms')
    else:
      # opening the login window
      self.create_room = Create_Room()
      self.create_room.show()
      # closing the current window
      self.close()

  def login(self):
    # checking if user already logged in
    if globals.current_user:
      QMessageBox.warning(self, 'Warning', f'You are already logged in as {globals.current_user}')
    else:
      # opening the login window
      self.login_ui = LoginUI()
      self.login_ui.show()
      # closing the current window
      self.close()

  def register(self):
    if globals.current_user:
      QMessageBox.warning(self, 'Warning', f'You are already logged in as {globals.current_user}')
    else:
      from register import Register
      # opening the login window
      self.register_ui = Register()
      self.register_ui.show()
      # closing the current window
      self.close()

# initialize the app
if __name__ == '__main__':
  app = QApplication(sys.argv)
  UIWindow = MainUI()
  app.exec_()