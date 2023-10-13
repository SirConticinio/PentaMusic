# Subclass QMainWindow to customize your application's main window
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QLineEdit, QLabel, QWidget
from pentamusic.basedatos.sql import SQL
from .menu import Menu
from pentamusic.basedatos.session import Session


class LoginWindow(Menu):
    def __init__(self, is_login):
        super().__init__()

        self.isLogin = is_login
        modeLabel = QLabel("INICIO DE SESIÓN" if is_login else "REGISTRO DE NUEVO USUARIO")
        usuarioLabel = QLabel("Introduce tu nombre de usuario:")
        self.usuarioBox = QLineEdit()
        self.usuarioBox.setMaxLength(16)
        self.usuarioBox.setPlaceholderText("[...]")
        contraseñaLabel = QLabel("Introduce tu contraseña:")
        self.contraseñaBox = QLineEdit()
        self.contraseñaBox.setPlaceholderText("[***]")
        self.contraseñaBox.setEchoMode(QLineEdit.Password)
        confirmar = QPushButton("Confirmar")
        confirmar.clicked.connect(lambda: self.confirm())

        layout = QVBoxLayout()
        self.add_back_button(layout, lambda: self.manager.open_init_menu())
        layout.addWidget(modeLabel)
        layout.addWidget(usuarioLabel)
        layout.addWidget(self.usuarioBox)
        layout.addWidget(contraseñaLabel)
        layout.addWidget(self.contraseñaBox)
        layout.addWidget(confirmar)

        self.set_layout(layout)

    def confirm(self):
        user = self.usuarioBox.text()
        password = self.contraseñaBox.text()
        print("User is ", user, ", password is ", password)

        if self.isLogin:
            print("Logueando!")
            # comprobamos si contraseña coincide con la de base de datos
            if self.crypto.login_user(user, password):
                print("Login correcto.")
                self.manager.open_main_menu()
        else:
            self.crypto.register_user(user, password)
            self.manager.open_main_menu()
            # metemos el usuario en la base de datos si no existe
