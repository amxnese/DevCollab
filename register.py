from PyQt5.QtWidgets import QMainWindow, QMessageBox, QLineEdit
from abstraction import Submitions
import sqlite3
from PyQt5 import uic, QtGui
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtCore import QRect
# keep track on what user is logged in
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

class Register(QMainWindow):
  def __init__(self):
    super(Register, self).__init__()
    uic.loadUi("register.ui", self)
    self.register_button.clicked.connect(self.submit)

    # setting the left arrow label
    self.label = ClickableLabel(self, self.centralwidget)
    self.label.setGeometry(QRect(10, 0, 47, 51))  # Set the geometry as per your requirements
    self.label.setAutoFillBackground(False)
    self.label.setText("")
    self.label.setPixmap(QtGui.QPixmap("arrow.svg"))
    self.label.setScaledContents(True)
    self.label.setObjectName("label")
    self.setMaximumSize(690, 375)
    self.setMinimumSize(690, 375)
    self.password_reg.setEchoMode(QLineEdit.Password) 

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