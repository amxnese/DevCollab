import sys
from PyQt6.QtWidgets import QApplication

from main_window import MainWindow
from styles import APP_STYLESHEET

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLESHEET)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
