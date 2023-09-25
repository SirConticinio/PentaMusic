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

        group = QWidget()
        groupLayout = QVBoxLayout()
        self.set_partituras(groupLayout)
        group.setLayout(groupLayout)

        scroll = QScrollArea()
        scroll.setWidget(group)
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(200)

        importar = QPushButton("Importar más partituras")
        importar.clicked.connect(lambda: self.clicked_importar())

        layout = QVBoxLayout()
        layout.addWidget(welcome)
        layout.addWidget(scroll)
        layout.addWidget(importar)
        self.container.setLayout(layout)

    def set_partituras(self, group: QVBoxLayout):
        # todo
        for i in range(10):
            nombre = "test nº" + str(i)
            label = QLabel(nombre)
            group.addWidget(label)

    def clicked_importar(self):
        # todo
        pass
