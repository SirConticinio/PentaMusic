# Subclass QMainWindow to customize your application's main window
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QLineEdit, QLabel, QWidget, QSpacerItem, QSizePolicy
from pentamusic.basedatos.sql import SQL
from .menu import Menu
from .sheet_menu import SheetWindow
from pentamusic.basedatos.session import Session


class MainWindow(Menu):
    def __init__(self):
        super().__init__()

        welcome = QLabel("¡Bienvenido, " + self.session.user + "!")
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        datos = QLabel("Accede a tus datos:")
        partituras = QPushButton("Partituras")
        partituras.clicked.connect(lambda: self.clicked_partituras())
        conciertos = QPushButton("Conciertos")
        conciertos.clicked.connect(lambda: self.clicked_conciertos())

        firmar = QPushButton("CRYPTO: Firmar usuario")
        firmar.clicked.connect(lambda: self.clicked_firmar())
        verificar = QPushButton("CRYPTO: Verificar usuario")
        verificar.clicked.connect(lambda: self.clicked_verificar())

        layout = QVBoxLayout()
        self.add_back_button(layout, lambda: self.clicked_logout(), "⊘ Cerrar sesión ⊘")
        layout.addWidget(welcome)
        layout.addSpacerItem(spacer)
        layout.addWidget(datos)
        layout.addWidget(partituras)
        layout.addWidget(conciertos)
        layout.addWidget(firmar)
        layout.addWidget(verificar)

        self.set_layout(layout)

    def clicked_logout(self):
        Session.revoke()
        self.manager.open_init_menu()

    def clicked_partituras(self):
        self.manager.open_sheet_menu()

    def clicked_conciertos(self):
        self.manager.open_concert_menu(False)

    def clicked_firmar(self):
        self.crypto.sign_user(self.session.user)

    def clicked_verificar(self):
        self.crypto.verify_user(self.session.user)
