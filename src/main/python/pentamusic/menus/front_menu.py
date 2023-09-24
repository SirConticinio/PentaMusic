# Subclass QMainWindow to customize your application's main window
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QLineEdit, QLabel, QWidget
from .login_menu import LoginWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PentaMusic")

        login = QPushButton("Iniciar sesión.")
        login.clicked.connect(self.clicked_login)
        register = QPushButton("Registrar nuevo usuario.")
        register.clicked.connect(self.clicked_register)

        layout = QVBoxLayout()
        layout.addWidget(login)
        layout.addWidget(register)

        container = QWidget()
        container.setLayout(layout)

        # Set the central widget of the Window.
        self.setCentralWidget(container)

    def clicked_login(self):
        self.loginWindow = LoginWindow(True)
        self.loginWindow.show()
        self.close()

    def clicked_register(self):
        self.loginWindow = LoginWindow(False)
        self.loginWindow.show()
        self.close()
