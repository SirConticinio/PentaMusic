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


class SheetEditWindow(Menu):
    def __init__(self, sheet_id):
        super().__init__()

        self.session = Session()
        welcome = QLabel("Edita los datos de la partitura y haz click en 'confirmar' para terminar:")
        sheet = self.datos.check_partitura(sheet_id)

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
        icon = ("✅" if sheet.is_public else "❌")
        publicLabel = QLabel("¿Es pública? -> " + icon)

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
        layout.addWidget(publicLabel)
        layout.addWidget(confirmar)

        self.container.setLayout(layout)

    def clicked_confirmar(self):
        # aquí volvemos a guardar la partitura
        pass
