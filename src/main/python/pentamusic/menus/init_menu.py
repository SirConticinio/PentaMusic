# Subclass QMainWindow to customize your application's main window
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QLineEdit, QLabel, QWidget, QSpacerItem, QSizePolicy
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

        spacer = QSpacerItem(20, 175, QSizePolicy.Minimum, QSizePolicy.Expanding)
        killtable = QPushButton("DEBUG: Borrar datos.")
        killtable.clicked.connect(lambda: self.clicked_delete())
        debug1 = QPushButton("DEBUG: Fake login Mario.")
        debug1.clicked.connect(lambda: self.clicked_debug_mario())
        debug2 = QPushButton("DEBUG: Fake login Álvaro.")
        debug2.clicked.connect(lambda: self.clicked_debug_alvaro())

        layout = QVBoxLayout()
        layout.addWidget(login)
        layout.addWidget(register)
        layout.addSpacerItem(spacer)
        layout.addWidget(debug1)
        layout.addWidget(debug2)
        layout.addWidget(killtable)

        self.set_layout(layout)

    def clicked_login(self):
        self.manager.open_login_menu(True)

    def clicked_register(self):
        self.manager.open_login_menu(False)

    def clicked_debug_mario(self):
        self.crypto.login_debug("Mario", "12345")
        self.manager.open_main_menu()

    def clicked_debug_alvaro(self):
        self.crypto.login_debug("Alvaro", "abcdefg")
        self.manager.open_main_menu()

    def clicked_delete(self):
        self.datos.reset()
