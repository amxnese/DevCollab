from PyQt5.QtWidgets import QMainWindow, QMessageBox
from abstraction import Submitions
import sqlite3
from PyQt5 import uic
import globals

# class LoginUI(QMainWindow, Submitions):
class LoginUI(QMainWindow):
  def __init__(self):
    super(LoginUI, self).__init__()
    uic.loadUi("login.ui", self)
    self.login_button.clicked.connect(self.submit)
    
  def home(self):
    self.close()
    # late import to avoid circular imports
    from main import MainUI
    self.mainWindow = MainUI()

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
      # conn.commit()
      conn.close()