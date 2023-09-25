# Subclass QMainWindow to customize your application's main window
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QLineEdit, QLabel, QWidget, QSpacerItem, QFormLayout, QScrollArea
from pentamusic.basedatos.sql import SQL
from .menu import Menu
from pentamusic.basedatos.session import Session


class SheetWindow(Menu):
    def __init__(self):
        super().__init__()

        self.session = Session()
        welcome = QLabel("Aquí tienes tu lista de partituras:")
        spacer = QSpacerItem(0, 30)

        group = QWidget()
        form = QFormLayout()
        self.set_partituras(form)
        group.setLayout(form)
        scroll = QScrollArea()
        scroll.setWidget(group)
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(200)
        layout = QVBoxLayout()
        layout.addWidget(scroll)
        self.container.setLayout(layout)

        importar = QPushButton("Importar más partituras")
        importar.clicked.connect(lambda: self.clicked_importar())

        layout = QVBoxLayout()
        layout.addWidget(welcome)
        layout.addWidget(spacer)
        layout.addWidget(importar)

        self.container.setLayout(layout)

    def set_partituras(self, form):
        # todo
        form.addRow("test1")
        form.addRow("test2")
        form.addRow("test3")
        form.addRow("test4")
        form.addRow("test5")
        form.addRow("test6")
        form.addRow("test7")

    def clicked_importar(self):
        # todo
        pass
