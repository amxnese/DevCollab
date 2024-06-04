from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QWidget
from room import Room
from PyQt5 import uic
import sqlite3
import globals

class Create_Room(QMainWindow):
    def setupUi(self, Create_Room_Window):
        Create_Room_Window.setObjectName("Create_Room_Window")
        Create_Room_Window.resize(470, 323)
        Create_Room_Window.setStyleSheet("#Create_Room_Window{\n"
                                         "    background-color: #6495ED;\n"
                                         "}")
        self.centralwidget = QtWidgets.QWidget(Create_Room_Window)
        self.centralwidget.setObjectName("centralwidget")

        # Create a vertical layout for the central widget
        self.central_layout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.central_layout.setContentsMargins(20, 20, 20, 20)
        self.central_layout.setSpacing(10)

        self.main_label = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.main_label.setFont(font)
        self.main_label.setStyleSheet("#main_label{\n"
                                      "    border-radius: 4px;\n"
                                      "}")
        self.main_label.setAlignment(QtCore.Qt.AlignCenter)
        self.main_label.setObjectName("main_label")
        self.central_layout.addWidget(self.main_label)

        self.name_label = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.name_label.setFont(font)
        self.name_label.setAlignment(QtCore.Qt.AlignCenter)
        self.name_label.setObjectName("name_label")
        self.central_layout.addWidget(self.name_label)

        self.room_name = QtWidgets.QLineEdit(self.centralwidget)
        self.room_name.setEnabled(True)
        self.room_name.setMinimumSize(QtCore.QSize(0, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.room_name.setFont(font)
        self.room_name.setStyleSheet("QLineEdit{\n"
                                     "padding-left : 4px;\n"
                                     "}")
        self.room_name.setInputMask("")
        self.room_name.setText("")
        self.room_name.setDragEnabled(False)
        self.room_name.setObjectName("room_name")
        self.central_layout.addWidget(self.room_name)

        self.CreateRoomButton = QtWidgets.QPushButton(self.centralwidget)
        self.CreateRoomButton.setMinimumSize(QtCore.QSize(0, 40))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.CreateRoomButton.setFont(font)
        self.CreateRoomButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.CreateRoomButton.setObjectName("CreateRoomButton")
        self.central_layout.addWidget(self.CreateRoomButton)

        Create_Room_Window.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(Create_Room_Window)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 470, 22))
        self.menubar.setObjectName("menubar")
        Create_Room_Window.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(Create_Room_Window)
        self.statusbar.setObjectName("statusbar")
        Create_Room_Window.setStatusBar(self.statusbar)

        self.retranslateUi(Create_Room_Window)
        QtCore.QMetaObject.connectSlotsByName(Create_Room_Window)

        ''' Logic '''
        self.CreateRoomButton.clicked.connect(self.submit)
    
    def submit(self):
			# getting the name of the project
      name = self.room_name.text()
			# checking if the name is valid
      if not name:
        QMessageBox.warning(self, 'Warning', 'Please enter the name of the room')
      else:
				# inserting the project to the database
        conn = sqlite3.connect("myDb.db")
        cur = conn.cursor()
        cur.execute('insert into Projects (username, name) values (?,?)',(globals.current_user, name))
				# getting the id of the last inserted project
        project_id =  cur.lastrowid
        conn.commit()
        conn.close()
        globals.message = ['information', f"Your project's id is {project_id}"]
        globals.current_project = project_id
        self.close()
        self.room_ui = Room()
        self.room_ui.setupUi(self)




    def retranslateUi(self, Create_Room_Window):
        _translate = QtCore.QCoreApplication.translate
        Create_Room_Window.setWindowTitle(_translate("Create_Room_Window", "MainWindow"))
        self.main_label.setText(_translate("Create_Room_Window", "Create a Room and invite your teammates"))
        self.name_label.setText(_translate("Create_Room_Window", "Give your room a name"))
        self.room_name.setPlaceholderText(_translate("Create_Room_Window", "type here..."))
        self.CreateRoomButton.setText(_translate("Create_Room_Window", "Create Room"))

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindowApp()
    main_window.show()
    sys.exit(app.exec_())

