# Subclass QMainWindow to customize your application's main window
import datetime
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


class ConcertWindow(Menu):
    def __init__(self, show_old: bool):
        super().__init__()

        welcome = QLabel("Aquí tienes tu lista de conciertos:")

        group = QWidget()
        groupLayout = QVBoxLayout()
        self.set_conciertos(groupLayout, show_old)
        group.setLayout(groupLayout)
        groupLayout.addStretch(1)
        group.adjustSize()

        scroll = QScrollArea()
        scroll.setWidget(group)
        scroll.setWidgetResizable(True)
        scroll.setMinimumSize(500, 200)

        pub = QPushButton("Añadir nuevo concierto")
        pub.clicked.connect(lambda: self.clicked_crear(self.session.user))
        arch = QPushButton("Ignorar conciertos antiguos" if show_old else "Mostrar conciertos antiguos")
        arch.clicked.connect(lambda: self.clicked_antiguos(not show_old))

        layout = QVBoxLayout()
        self.add_back_button(layout, lambda: self.manager.open_main_menu())
        layout.addWidget(welcome)
        layout.addWidget(scroll)
        layout.addWidget(pub)
        layout.addWidget(arch)
        self.set_layout(layout)

    def set_conciertos(self, group: QVBoxLayout, show_old: bool):
        concerts = self.datos.get_user_concerts(self.session.user)
        for concert in concerts:
            # mostramos conciertos viejos solo si lo hemos elegido, si no solo conciertos recientes y futuros
            if show_old or concert.date > (datetime.datetime.now() - datetime.timedelta(1)):
                user = concert.user
                dt = concert.date
                sheet_info = concert.title if concert.title != "" else "Sin título"
                sheet_info += "\nFecha y hora: " + str(concert.date.strftime("%d/%m/%Y, %H:%M:%S"))
                sheet_info += "\nLugar: " + (concert.place if concert.place != "" else "Desconocido")
                view = QPushButton(sheet_info)
                view.setStyleSheet("padding:8px")
                view.clicked.connect(lambda c=False, us=user, dt=dt: self.clicked_open(us,dt))
                group.addWidget(view)

    def clicked_antiguos(self, show_old):
        self.manager.open_concert_menu(show_old)

    def clicked_open(self, user, date):
        self.manager.open_concert_edit_menu(user, date)

    def clicked_crear(self, user):
        date = datetime.datetime.now()
        self.datos.insertar_concerts(user, "", date, "")
        self.manager.open_concert_edit_menu(user, date)
