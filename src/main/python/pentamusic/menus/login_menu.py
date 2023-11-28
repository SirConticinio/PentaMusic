# Subclass QMainWindow to customize your application's main window
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QLineEdit, QLabel, QWidget
from pentamusic.basedatos.sql import SQL
from .dialog import OkDialog
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
        passwordLabel = QLabel("Introduce tu contraseña:")
        self.passwordBox = QLineEdit()
        self.passwordBox.setPlaceholderText("[***]")
        self.passwordBox.setEchoMode(QLineEdit.Password)
        confirmar = QPushButton("Confirmar")
        confirmar.clicked.connect(lambda: self.confirm())

        layout = QVBoxLayout()
        self.add_back_button(layout, lambda: self.manager.open_init_menu())
        layout.addWidget(modeLabel)
        layout.addWidget(usuarioLabel)
        layout.addWidget(self.usuarioBox)
        layout.addWidget(passwordLabel)
        layout.addWidget(self.passwordBox)
        layout.addWidget(confirmar)

        self.set_layout(layout)

    def confirm(self):
        user = self.usuarioBox.text()
        password = self.passwordBox.text()

        # Ahora validamos la entrada de usuario y contraseña
        user_valid = False
        if len(user) > 32:
            OkDialog("¡El nombre de usuario solo puede tener 32 caracteres como máximo!")
        elif len(user) <= 0:
            OkDialog("¡El nombre de usuario no puede estar vacío!")
        else:
            user_valid = True

        password_valid = False
        if len(password) < 8:
            OkDialog("¡La contraseña debe tener un mínimo de 8 caracteres!")
        else:
            password_valid = True

        if user_valid and password_valid:
            if self.isLogin:
                print("Logueando!")
                # comprobamos si contraseña coincide con la de base de datos
                if self.crypto.login_user(user, password):
                    print("Login correcto.")
                    self.manager.open_main_menu()
            else:
                # metemos el usuario en la base de datos si no existe
                if self.crypto.register_user(user, password):
                    self.manager.open_main_menu()
