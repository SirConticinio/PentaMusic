# Subclass QMainWindow to customize your application's main window
import os
import shutil
import uuid

from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QLineEdit, QLabel, QWidget, QSpacerItem, QScrollArea, QFileDialog
from pentamusic.basedatos.sql import SQL
from .menu import Menu
from pentamusic.basedatos.session import Session
from .sheet_edit_menu import SheetEditWindow


class SheetWindow(Menu):
    def __init__(self):
        super().__init__()

        self.session = Session()
        welcome = QLabel("Aquí tienes tu lista de partituras:")

        group = QWidget()
        groupLayout = QVBoxLayout()
        self.set_partituras(groupLayout)
        group.setLayout(groupLayout)

        scroll = QScrollArea()
        scroll.setWidget(group)
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(200)

        pub = QPushButton("Importar partitura pública")
        pub.clicked.connect(lambda: self.clicked_importar_publica())
        arch = QPushButton("Importar partitura desde archivo")
        arch.clicked.connect(lambda: self.clicked_importar_archivo(arch))

        layout = QVBoxLayout()
        layout.addWidget(welcome)
        layout.addWidget(scroll)
        layout.addWidget(pub)
        layout.addWidget(arch)
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
        originalname = os.path.basename(filename)
        newname = str(uuid.uuid4())
        path = home + "/" + newname
        shutil.copy2(filename, path)

        self.datos.insertar_partituras(newname, originalname, False, self.session.user, "", "")
        # todo guardar asociación

        # y ahora abrimos el menú de edición
        SheetEditWindow(newname)
