# Subclass QMainWindow to customize your application's main window
import os
import shutil
import uuid

from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QLineEdit, QLabel, QWidget, QSpacerItem, QScrollArea, QFileDialog
from pentamusic.basedatos.sql import SQL
from .menu import Menu
from pentamusic.basedatos.session import Session


class SheetEditWindow(Menu):
    def __init__(self, sheet_id):
        super().__init__()



        self.session = Session()
        welcome = QLabel("Edita los datos de la partitura y haz click en 'confirmar' para terminar:")

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

    def set_partituras(self, group: QVBoxLayout):
        # todo
        for i in range(10):
            nombre = "test nº" + str(i)
            label = QLabel(nombre)
            group.addWidget(label)

    def clicked_importar_publica(self):
        # todo
        pass

    def clicked_importar_archivo(self, arch):
        file, _ = QFileDialog.getOpenFileName(arch, "Elige un archivo de partitura", "", "PDF (*.pdf);;PNG (*.png);;All Files (*);;")
        if file:
            print(file)
            self.save_sheet(file)

    def save_sheet(self, filename):
        home = os.path.expanduser("~/PentaMusic/Sheets")
        if not os.path.exists(home):
            os.makedirs(home)

        # aqui lo guardamos con un nombre random, pero en la base de datos se guarda el original
        newname = str(uuid.uuid4())
        path = home + "/" + newname
        shutil.copy2(filename, path)



