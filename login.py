from PyQt5.QtWidgets import QMainWindow, QMessageBox, QLineEdit
from abstraction import Submitions
import sqlite3
from PyQt5 import uic, QtGui
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtCore import QRect
import globals

class ClickableLabel(QLabel):
    def __init__(self, login_ui, *args, **kwargs):
        super(ClickableLabel, self).__init__(*args, **kwargs)
        self.setCursor(Qt.PointingHandCursor)
        self.login_ui = login_ui

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
          from main import MainUI
          self.main_window = MainUI()
          self.main_window.show()
          self.login_ui.close()
class LoginUI(QMainWindow):
  def __init__(self):
    super(LoginUI, self).__init__()
    uic.loadUi("login.ui", self)
    # connecting the login button to an event
    self.login_button.clicked.connect(self.submit)

    # replacing the regular label to a label that has an event
    self.label = ClickableLabel(self, self.centralwidget)
    self.label.setGeometry(QRect(10, 0, 47, 51)) 
    self.label.setAutoFillBackground(False)
    self.label.setText("")
    self.label.setPixmap(QtGui.QPixmap("arrow.svg"))
    self.label.setScaledContents(True)
    self.label.setObjectName("label")
    self.setMaximumSize(690, 375)
    self.setMinimumSize(690, 375)
    self.password_login.setEchoMode(QLineEdit.Password) 
    
  def home(self):
    self.close()
    from main import MainUI
    self.mainWindow = MainUI()
    self.mainWindow.show()

  def submit(self):
    # check if username input is not empty
    if not self.username_login.text():
      QMessageBox.warning(self, 'Warning', 'Please enter your username')
    # check if password is not empty
    elif not self.password_login.text():
      QMessageBox.warning(self, 'Warning', 'Please enter your password')
    # case where username and password are not empty
    else:
      # fetching user inputs 
      username_input = self.username_login.text()
      password_input = self.password_login.text()

      # connecting to the database
      conn = sqlite3.connect('myDb.db')
      cursor = conn.cursor()

      # grabing information from database
      cursor.execute(f"select * from users where username = '{username_input}'")
      query = cursor.fetchone()

      # checking if the username exists in database
      if query:
        username, password = query[0], query[1]

        # checking if the password of the username matches the user's input
        if password_input == password:
          # updating the logged in user
          globals.current_user = username

          # returning to home page
          self.home()

          QMessageBox.information(self, 'Success', f"logged in as {username}")
        
        # wrong password
        else:
          QMessageBox.warning(self, 'Warning', f'Incorrect password for {username_input}')
      # query is None : no such username in database
      else:
        QMessageBox.warning(self, 'Warning', f'Wrong username')
        
      # commiting changes and closing database
      conn.commit()
      conn.close()


