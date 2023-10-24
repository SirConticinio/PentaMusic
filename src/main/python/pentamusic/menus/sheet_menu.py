# Subclass QMainWindow to customize your application's main window
import os
import shutil
import subprocess
import sys
import uuid

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QLineEdit, QLabel, QWidget, QSpacerItem, QScrollArea, QFileDialog, \
    QHBoxLayout
from pentamusic.basedatos.sql import SQL
from .menu import Menu
from pentamusic.basedatos.session import Session
from pentamusic.menus.sheet_edit_menu import SheetEditWindow


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
            sheet_info = user_sheet.sheet.title
            sheet_info += "\nCompositor: " + user_sheet.sheet.composer
            sheet_info += "\nInstrumentos: " + user_sheet.sheet.instrument
            sheet_info += "\n\nCompás aprendido: " + str(user_sheet.learned_bar)
            sheet_info += "\nComentarios: " + (user_sheet.comments if user_sheet.comments is not None else "-")
            view = QPushButton(sheet_info)
            view.setStyleSheet("text-align:left; padding:8px")
            view.clicked.connect(lambda c=False, sid=sheet_id: self.clicked_open(sid))
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
            self.save_sheet(file)

    def clicked_edit(self, sheet_id):
        self.manager.open_usersheet_edit_menu(sheet_id)

    def clicked_open(self, sheet_id):
        path = os.path.expanduser("~/PentaMusic/Sheets/" + sheet_id + ".pdf")
        self.open_file(path)

    def save_sheet(self, filename):
        home = os.path.expanduser("~/PentaMusic/Sheets")
        if not os.path.exists(home):
            os.makedirs(home)

        # aqui lo guardamos con un nombre random, pero en la base de datos se guarda el original
        originalname = os.path.basename(filename).removesuffix(".pdf")
        newname = str(uuid.uuid4())
        path = home + "/" + newname + ".pdf"
        shutil.copy2(filename, path)

        self.datos.insertar_partituras(newname, originalname, self.session.user, False, "", "")

        # y ahora abrimos el menú de edición
        self.manager.open_usersheet_edit_menu(newname)
