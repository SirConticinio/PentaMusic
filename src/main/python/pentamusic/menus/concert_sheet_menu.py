# Subclass QMainWindow to customize your application's main window
import os
import shutil
import subprocess
import sys
import uuid

from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QLineEdit, QLabel, QWidget, QSpacerItem, QScrollArea, QFileDialog, \
    QHBoxLayout
from pentamusic.basedatos.sql import SQL
from .menu import Menu
from pentamusic.basedatos.session import Session
from pentamusic.menus.sheet_edit_menu import SheetEditWindow


class ConcertSheetWindow(Menu):
    def __init__(self, user, date):
        super().__init__()
        self.user = user
        self.date = date

        welcome = QLabel("Aquí están tus partituras:")

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

        layout = QVBoxLayout()
        self.add_back_button(layout, lambda: self.manager.open_concert_edit_menu(user, date))
        layout.addWidget(welcome)
        layout.addWidget(scroll)
        self.set_layout(layout)

    def set_partituras(self, group: QVBoxLayout):
        added_sheets = self.datos.get_all_concertsheets(self.user, self.date)

        my_sheets = self.datos.get_all_usersheets(self.session.user)
        for sheet in my_sheets:
            # la añadimos solo si no está ya programada en el concierto
            if not self.find_partitura(added_sheets, sheet.sheet.sheet_id):
                row = QWidget()
                layout = QHBoxLayout()
                imp = QPushButton("Importar")
                imp.setFixedWidth(80)
                sheet_id = sheet.sheet.sheet_id
                imp.clicked.connect(lambda c=False, sid=sheet_id: self.clicked_import(sid))
                view = QPushButton(sheet.sheet.title)
                view.clicked.connect(lambda c=False, sid=sheet_id: self.clicked_open(sid))
                layout.addWidget(imp)
                layout.addWidget(view)
                row.setLayout(layout)
                group.addWidget(row)

    def find_partitura(self, my_sheets, sheet_id):
        for sheet in my_sheets:
            if sheet.sheet_id == sheet_id:
                return True
        return False

    def clicked_import(self, sheet_id):
        self.datos.insertar_concertsheets(self.user, self.date, sheet_id)
        print("Partitura importada.")
        self.manager.open_concert_sheets_menu(self.user, self.date)

    def clicked_open(self, sheet_id):
        path = os.path.expanduser("~/PentaMusic/Sheets/" + sheet_id + ".pdf")
        self.open_file(path)
