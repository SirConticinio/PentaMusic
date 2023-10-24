# Subclass QMainWindow to customize your application's main window
import os
import shutil
import uuid

from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QLineEdit, QLabel, QWidget, QSpacerItem, QScrollArea, QFileDialog, \
    QCheckBox
from pentamusic.basedatos.sql import SQL
from .menu import Menu
from pentamusic.basedatos.session import Session


class SheetEditWindow(Menu):
    def __init__(self, sheet_id):
        super().__init__()

        welcome = QLabel("Edita los datos de la partitura y haz click en 'confirmar' para terminar:")
        sheet = self.datos.get_sheet(sheet_id)
        self.sheet = sheet
        self.sheet_id = sheet_id
        self.owner = sheet.owner

        titleLabel = QLabel("Título:")
        self.title = QLineEdit()
        self.title.setText(sheet.title)
        composerLabel = QLabel("Compositor:")
        self.composer = QLineEdit()
        self.composer.setText(sheet.composer)
        instrumentLabel = QLabel("Instrumento:")
        self.instrument = QLineEdit()
        self.instrument.setText(sheet.instrument)
        barsLabel = QLabel("Número de compases:")
        self.bars = QLineEdit()
        self.bars.setText(str(sheet.bars))
        self.bars.setValidator(QIntValidator())
        self.public = QCheckBox("¿Es pública?")
        self.public.setChecked(sheet.is_public)

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
        layout.addWidget(barsLabel)
        layout.addWidget(self.bars)
        layout.addWidget(self.public)
        layout.addWidget(confirmar)

        self.set_layout(layout)

    def clicked_confirmar(self):
        # aquí volvemos a guardar la partitura
        is_public_now = 0 if self.public.checkState() == 0 else 1
        self.datos.update_sheet(self.sheet_id, self.title.text(), self.owner, is_public_now, self.sheet.file_nonce, self.composer.text(),
                                self.instrument.text(), self.bars.text())

        # encriptamos / desencriptamos si cambia el estado de la partitura
        should_encrypt = (not is_public_now) and self.sheet.is_public
        should_decrypt = is_public_now and (not self.sheet.is_public)
        if should_encrypt or should_decrypt:
            print("¡Cambiando el estado de la partitura!")
            self.save_sheet(self.get_sheet_path(self.sheet_id), should_encrypt, should_decrypt, False, self.sheet_id, self.sheet.file_nonce)

        # y volvemos al menú de antes
        self.manager.open_sheet_menu()
