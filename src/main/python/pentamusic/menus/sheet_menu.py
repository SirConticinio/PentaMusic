# Subclass QMainWindow to customize your application's main window
import os
import shutil
import subprocess
import sys
import tempfile
import uuid

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QLineEdit, QLabel, QWidget, QSpacerItem, QScrollArea, QFileDialog, \
    QHBoxLayout
from pentamusic.basedatos.sql import SQL
from .menu import Menu
from pentamusic.basedatos.session import Session
from pentamusic.menus.sheet_edit_menu import SheetEditWindow
from ..crypto import Crypto


class SheetWindow(Menu):
    def __init__(self):
        super().__init__()

        welcome = QLabel("Aquí tienes tu lista de partituras:")

        group = QWidget()
        groupLayout = QVBoxLayout()
        self.set_partituras(groupLayout)
        group.setLayout(groupLayout)
        groupLayout.addStretch(1)
        group.adjustSize()

        scroll = QScrollArea()
        scroll.setWidget(group)
        scroll.setWidgetResizable(True)
        scroll.setMinimumSize(500, 200)

        pub = QPushButton("Importar partitura pública")
        pub.clicked.connect(lambda: self.clicked_importar_publica())
        arch = QPushButton("Importar partitura desde archivo")
        arch.clicked.connect(lambda: self.clicked_importar_archivo(arch))

        layout = QVBoxLayout()
        self.add_back_button(layout, lambda: self.manager.open_main_menu())
        layout.addWidget(welcome)
        layout.addWidget(scroll)
        layout.addWidget(pub)
        layout.addWidget(arch)
        self.set_layout(layout)

    def set_partituras(self, group: QVBoxLayout):
        sheets = self.datos.get_all_usersheets(self.session.user)
        for user_sheet in sheets:
            row = QWidget()
            layout = QHBoxLayout()
            edit = QPushButton("Editar")
            edit.setFixedWidth(80)
            sheet_id = user_sheet.sheet.sheet_id
            edit.clicked.connect(lambda c=False, sid=sheet_id: self.clicked_edit(sid))

            learned = int(user_sheet.learned_bar) if user_sheet.learned_bar != "" else 0
            porcentaje = str(round((learned/user_sheet.sheet.bars)*100, 2)) + "%" if user_sheet.sheet.bars > 0 else "?%"
            compositor = user_sheet.sheet.composer if user_sheet.sheet.composer != "" else "<Sin especificar>"
            instrumentos = user_sheet.sheet.instrument if user_sheet.sheet.instrument != "" else "<Sin especificar>"
            sheet_info = user_sheet.sheet.title
            sheet_info += "\nCompositor: " + compositor
            sheet_info += "\nInstrumentos: " + instrumentos
            sheet_info += "\n\nPorcentaje aprendido: " + porcentaje
            sheet_info += "\nComentarios: " + (user_sheet.comments if user_sheet.comments != "" else "[...]")
            view = QPushButton(sheet_info)
            view.setStyleSheet("text-align:left; padding:8px")
            view.clicked.connect(lambda c=False, sid=user_sheet.sheet: self.clicked_open(sid))
            layout.addWidget(edit)
            layout.addWidget(view)
            row.setLayout(layout)
            group.addWidget(row)

    def clicked_importar_publica(self):
        self.manager.open_sheet_public_menu()

    def clicked_importar_archivo(self, arch):
        file, _ = QFileDialog.getOpenFileName(arch, "Elige un archivo de partitura", "", "PDF (*.pdf);;PNG (*.png);;All Files (*);;")
        if file:
            print(file)
            self.save_sheet(file, True, False, True, "")

    def clicked_edit(self, sheet_id):
        self.manager.open_usersheet_edit_menu(sheet_id)

    def clicked_open(self, sheet):
        self.open_sheet(sheet)
