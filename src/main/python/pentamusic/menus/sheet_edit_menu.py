# Subclass QMainWindow to customize your application's main window
import os
import shutil
import uuid

from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QLineEdit, QLabel, QWidget, QSpacerItem, QScrollArea, QFileDialog, \
    QCheckBox
from pentamusic.basedatos.sql import SQL
from .menu import Menu
from pentamusic.basedatos.session import Session
from .sheet_menu import SheetWindow


class SheetEditWindow(Menu):
    def __init__(self, sheet_id):
        super().__init__()

        self.session = Session()
        welcome = QLabel("Edita los datos de la partitura y haz click en 'confirmar' para terminar:")
        sheet = self.datos.check_partitura(sheet_id)
        self.sheet_id = sheet_id

        titleLabel = QLabel("Título:")
        self.title = QLineEdit()
        self.title.setText(sheet.title)
        composerLabel = QLabel("Compositor:")
        self.composer = QLineEdit()
        self.composer.setText(sheet.composer)
        instrumentLabel = QLabel("Instrumento:")
        self.instrument = QLineEdit()
        self.instrument.setText(sheet.instrument)
        ownerLabel = QLabel("Dueño:")
        self.owner = QLineEdit()
        print(sheet.owner)
        self.owner.setText(sheet.owner)
        self.owner.setReadOnly(True)
        self.public = QCheckBox("¿Es pública?")
        self.public.setCheckState(False)

        confirmar = QPushButton("Confirmar")
        confirmar.clicked.connect(lambda: self.clicked_confirmar())

        layout = QVBoxLayout()
        layout.addWidget(welcome)
        layout.addWidget(titleLabel)
        layout.addWidget(self.title)
        layout.addWidget(composerLabel)
        layout.addWidget(self.composer)
        layout.addWidget(instrumentLabel)
        layout.addWidget(self.instrument)
        layout.addWidget(ownerLabel)
        layout.addWidget(self.owner)
        layout.addWidget(self.public)
        layout.addWidget(confirmar)

        self.container.setLayout(layout)

    def clicked_confirmar(self):
        # aquí volvemos a guardar la partitura
        ispublic = 0 if self.public.checkState() == 0 else 1
        print("La x es: ")
        print(ispublic)
        self.datos.actualizar_partituras(self.sheet_id, self.title.text(), self.owner.text(), ispublic, self.composer.text(),
                                         self.instrument.text())
        SheetWindow()
