from PyQt5.QtWidgets import QMainWindow, QMessageBox
from abstraction import Submitions
from PyQt5 import uic
import sqlite3

# keep track on what user is logged in
import globals

# class Register(QMainWindow, Submitions):
class Register(QMainWindow):
  def __init__(self):
    super(Register, self).__init__()
    uic.loadUi("register.ui", self)
    self.register_button.clicked.connect(self.submit)

  def home(self):
    self.close()
    # late import to avoid circular imports
    from main import MainUI
    self.mainWindow = MainUI()
    
  def submit(self):
    if not self.username_reg.text():
      QMessageBox.warning(self, 'Warning', 'Please enter your username')
    elif not self.password_reg.text():
      QMessageBox.warning(self, 'Warning', 'Please enter your password')
    else:
      # fetching the user credentials
      username = self.username_reg.text()
      password = self.password_reg.text()
      
      # connecting to the database
      conn = sqlite3.connect('myDb.db')
      cursor = conn.cursor()

      try:
        # inserting user database into the database
        cursor.execute(f"insert into users values(?, ?)" , (username, password))
        
        # keeping track of the logged in user
        globals.current_user = username

        # returning the home page
        self.home()

        # informing the user that his credentials was successfully added
        QMessageBox.information(self, 'Success', f'an account for {username} was successfully created')

      except sqlite3.IntegrityError as e:
        # informing the user about the error
        QMessageBox.warning(self, f'{e}', f"username '{username}' already exists")
        # clearing inputs
        self.username_reg.clear()
        self.password_reg.clear()

      # commiting changes to the database
      conn.commit()

      # closing the database
      conn.close()