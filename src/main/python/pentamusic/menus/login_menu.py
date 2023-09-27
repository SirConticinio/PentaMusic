# Subclass QMainWindow to customize your application's main window
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QLineEdit, QLabel, QWidget
from pentamusic.basedatos.sql import SQL
from .main_menu import MainWindow
from .menu import Menu
from pentamusic.basedatos.session import Session


class LoginWindow(Menu):
    def __init__(self, isLogin):
        super().__init__()

        self.isLogin = isLogin
        modeLabel = QLabel("INICIO DE SESIÓN" if isLogin else "REGISTRO DE NUEVO USUARIO")
        usuarioLabel = QLabel("Introduce tu nombre de usuario:")
        self.usuarioBox = QLineEdit()
        self.usuarioBox.setMaxLength(16)
        self.usuarioBox.setPlaceholderText("[...]")
        contraseñaLabel = QLabel("Introduce tu contraseña:")
        self.contraseñaBox = QLineEdit()
        self.contraseñaBox.setPlaceholderText("[***]")
        self.contraseñaBox.setEchoMode(QLineEdit.Password)
        confirmar = QPushButton("Confirmar")
        print("Connecting confirm2 to confirmar button")
        confirmar.clicked.connect(lambda: self.confirm())

        layout = QVBoxLayout()
        layout.addWidget(modeLabel)
        layout.addWidget(usuarioLabel)
        layout.addWidget(self.usuarioBox)
        layout.addWidget(contraseñaLabel)
        layout.addWidget(self.contraseñaBox)
        layout.addWidget(confirmar)

        self.container.setLayout(layout)

    def confirm(self):
        user = self.usuarioBox.text()
        password = self.contraseñaBox.text()
        print("User is ", user, ", password is ", password)

        if self.isLogin:
            print("Logueando!")
            # comprobamos si contraseña coincide con la de base de datos
            res = self.datos.consultar_login(user, password)
            if res:
                print("Login correcto.")
                Session.set_session(user, password)
                MainWindow()
            else:
                print("Login incorrecto.")
        else:
            self.datos.insertar_usuario(user, password)
            Session.set_session(user, password)
            print("Registrando!")
            MainWindow()
            # metemos el usuario en la base de datos si no existe
