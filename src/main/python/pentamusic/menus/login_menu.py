# Subclass QMainWindow to customize your application's main window
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QLineEdit, QLabel, QWidget


class LoginWindow(QMainWindow):
    def __init__(self, isLogin):
        super().__init__()

        self.isLogin = isLogin
        self.setWindowTitle("PentaMusic: Login")

        modeLabel = QLabel("INICIO DE SESIÓN" if isLogin else "REGISTRO DE NUEVO USUARIO")
        usuarioLabel = QLabel("Introduce tu nombre de usuario:")
        self.usuarioBox = QLineEdit()
        self.usuarioBox.setMaxLength(16)
        self.usuarioBox.setPlaceholderText("[...]")
        contraseñaLabel = QLabel("Introduce tu contraseña:")
        self.contraseñaBox = QLineEdit()
        self.contraseñaBox.setPlaceholderText("[***]")
        confirmar = QPushButton("Confirmar")
        confirmar.clicked.connect(self.confirm)

        layout = QVBoxLayout()
        layout.addWidget(modeLabel)
        layout.addWidget(usuarioLabel)
        layout.addWidget(self.usuarioBox)
        layout.addWidget(contraseñaLabel)
        layout.addWidget(self.contraseñaBox)
        layout.addWidget(confirmar)

        container = QWidget()
        container.setLayout(layout)

        # Set the central widget of the Window.
        self.setCentralWidget(container)

    def confirm(self):
        user = self.usuarioBox.text()
        password = self.contraseñaBox.text()
        print("User is ", user, ", password is ", password)

        if self.isLogin:
            print("Logueando!")
            # comprobamos si contraseña coincide con la de base de datos

        else:
            print("Registrando!")
            # metemos el usuario en la base de datos si no existe
