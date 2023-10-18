# Subclass QMainWindow to customize your application's main window
import os
import shutil
import uuid

from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QLineEdit, QLabel, QWidget, QSpacerItem, QScrollArea, QFileDialog, \
    QCheckBox, QSizePolicy
from pentamusic.basedatos.sql import SQL
from .dialog import YesNoDialog
from .menu import Menu
from pentamusic.basedatos.session import Session


class UserSheetEditWindow(Menu):
    def __init__(self, sheet_id):
        super().__init__()

        user_sheet = self.datos.get_usersheet(self.session.user, sheet_id)
        welcome = QLabel(user_sheet.sheet.title)
        self.sheet_id = sheet_id

        commentLabel = QLabel("Comentarios de la partitura:")
        self.comments = QLineEdit()
        self.comments.setText(user_sheet.sheet.title)
        learnedLabel = QLabel("Compás aprendido:")
        self.learned_bar = QLineEdit()
        self.learned_bar.setText(str(user_sheet.learned_bar))
        self.learned_bar.setValidator(QIntValidator())

        edit = QPushButton("Editar metadatos de la partitura")
        edit.clicked.connect(lambda: self.clicked_edit())
        delete = QPushButton("Eliminar partitura")
        delete.clicked.connect(lambda: self.clicked_delete())
        confirm = QPushButton("Confirmar cambios")
        confirm.clicked.connect(lambda: self.clicked_confirmar())

        layout = QVBoxLayout()
        layout.addWidget(welcome)
        layout.addWidget(commentLabel)
        layout.addWidget(self.comments)
        layout.addWidget(learnedLabel)
        layout.addWidget(self.learned_bar)
        layout.addWidget(confirm)

        spacer = QSpacerItem(20, 175, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addSpacerItem(spacer)
        if user_sheet.user == user_sheet.sheet.owner:
            layout.addWidget(edit)
        layout.addWidget(delete)

        self.set_layout(layout)

    def clicked_confirmar(self):
        # aquí volvemos a guardar la partitura
        self.actualizar_partitura()
        self.manager.open_sheet_menu()

    def actualizar_partitura(self):
        self.datos.actualizar_usersheet(self.sheet_id, self.session.user, self.comments.text(), self.learned_bar.text())

    def clicked_delete(self):
        # aquí borramos la partitura si hace falta
        YesNoDialog(
            "¿Estás seguro de que quieres borrar esta partitura de tu biblioteca?\nSi es una partitura pública y eres el dueño, también se borrará de las bibliotecas del resto de usuarios.",
            lambda: self.clicked_delete_yes(), lambda: ()
        )

    def clicked_delete_yes(self):
        self.datos.delete_usersheet(self.sheet_id, self.session.user)
        self.manager.open_sheet_menu()

    def clicked_edit(self):
        self.actualizar_partitura()
        self.manager.open_sheet_edit_menu(self.sheet_id)
