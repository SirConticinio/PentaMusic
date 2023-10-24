# Subclass QMainWindow to customize your application's main window
import datetime
import os
import shutil
import uuid

from PyQt5.QtCore import QSize, QDateTime
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QLineEdit, QLabel, QWidget, QSpacerItem, QScrollArea, QFileDialog, \
    QCheckBox, QSizePolicy, QDateEdit, QDateTimeEdit, QHBoxLayout
from pentamusic.basedatos.sql import SQL
from .dialog import YesNoDialog
from .menu import Menu
from pentamusic.basedatos.session import Session


class ConcertEditWindow(Menu):
    def __init__(self, user, date):
        super().__init__()
        self.user = user
        self.date = date

        concert = self.datos.get_concert(user, date)
        welcome = QLabel("Aquí está la información del concierto:")

        titleLabel = QLabel("Título del concierto:")
        self.title = QLineEdit()
        self.title.setText(concert.title)
        dateLabel = QLabel("Fecha del concierto:")
        self.date_edit = QDateTimeEdit(self.date)
        self.date_edit.setDisplayFormat("d/M/yyyy h:mm")
        self.date_edit.setCalendarPopup(True)
        placeLabel = QLabel("Lugar:")
        self.place = QLineEdit()
        self.place.setText(concert.place)

        edit = QPushButton("Importar partituras al concierto")
        edit.clicked.connect(lambda: self.clicked_import_sheets())
        delete = QPushButton("Eliminar concierto")
        delete.clicked.connect(lambda: self.clicked_delete())
        confirm = QPushButton("Confirmar cambios")
        confirm.clicked.connect(lambda: self.clicked_confirmar())

        layout = QVBoxLayout()
        layout.addWidget(welcome)
        layout.addWidget(titleLabel)
        layout.addWidget(self.title)
        layout.addWidget(dateLabel)
        layout.addWidget(self.date_edit)
        layout.addWidget(placeLabel)
        layout.addWidget(self.place)
        self.add_sheet_widget(layout)
        layout.addWidget(edit)
        layout.addWidget(confirm)

        spacer = QSpacerItem(20, 175, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addSpacerItem(spacer)
        layout.addWidget(delete)

        self.set_layout(layout)

    def add_sheet_widget(self, layout: QVBoxLayout):
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
        layout.addWidget(scroll)

    def set_partituras(self, group: QVBoxLayout):
        added_sheets = self.datos.get_all_concertsheets(self.user, self.date)

        for sheet in added_sheets:
            row = QWidget()
            layout = QHBoxLayout()
            imp = QPushButton("Desvincular")
            imp.setFixedWidth(80)
            sheet_id = sheet.sheet_id
            imp.clicked.connect(lambda c=False, sid=sheet_id: self.clicked_desvincular(sid))
            view = QPushButton(sheet.title)
            view.clicked.connect(lambda c=False, sid=sheet: self.clicked_open(sid))
            layout.addWidget(imp)
            layout.addWidget(view)
            row.setLayout(layout)
            group.addWidget(row)

    def clicked_desvincular(self, sheet_id):
        self.datos.delete_concertsheets(self.user, self.date, sheet_id)
        self.update_concert()
        self.manager.open_concert_edit_menu(self.user, self.date)

    def clicked_open(self, sheet):
        self.open_sheet(sheet)

    def clicked_confirmar(self):
        # aquí volvemos a guardar el concierto
        self.update_concert()
        self.manager.open_concert_menu(False)

    def update_concert(self):
        original_date = self.date
        self.date = self.date_edit.dateTime().toPyDateTime()
        self.datos.update_concert(self.user, self.title.text(), self.date, self.place.text(), original_date)

    def clicked_delete(self):
        # aquí borramos la partitura si hace falta
        YesNoDialog(
            "¿Estás seguro de que quieres borrar este concierto de tu biblioteca?\nEsta acción no se puede deshacer.",
            lambda: self.clicked_delete_yes(), lambda: ()
        )

    def clicked_delete_yes(self):
        self.datos.delete_concert(self.user, self.date)
        self.manager.open_concert_menu(False)

    def clicked_import_sheets(self):
        self.update_concert()
        self.manager.open_concert_sheets_menu(self.user, self.date)
