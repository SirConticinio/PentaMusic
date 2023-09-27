# Subclass QMainWindow to customize your application's main window
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QLineEdit, QLabel, QWidget
from .login_menu import LoginWindow
from .main_menu import MainWindow
from .menu import Menu

class InitWindow(Menu):
    def __init__(self):
        super().__init__()

        login = QPushButton("Iniciar sesión.")
        login.clicked.connect(lambda: self.clicked_login())
        register = QPushButton("Registrar nuevo usuario.")
        register.clicked.connect(lambda: self.clicked_register())

        layout = QVBoxLayout()
        layout.addWidget(login)
        layout.addWidget(register)

        self.container.setLayout(layout)

    def clicked_login(self):
        LoginWindow(True)

    def clicked_register(self):
        LoginWindow(False)
