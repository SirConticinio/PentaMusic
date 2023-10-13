import os
import subprocess
import sys

from PyQt5.QtWidgets import QMainWindow, QWidget, QPushButton, QBoxLayout, QApplication
from pentamusic.basedatos.sql import SQL
from pentamusic.crypto import Crypto
from pentamusic.menu_manager import MenuManager


class Menu:
    def __init__(self, is_separate_window=False):
        if not is_separate_window:
            self.w = self.get_window()
        else:
            self.w = QMainWindow()

        self.setup_window()
        self.datos = SQL()
        self.crypto = Crypto()
        self.manager = MenuManager()
        self.w.show()

    def setup_window(self):
        self.w.setWindowTitle("PentaMusic")
        if self.w.centralWidget() is not None:
            self.w.centralWidget().destroy()

        # Set the central widget of the Window.
        self.container = QWidget()
        self.w.setCentralWidget(self.container)

    def set_layout(self, layout):
        self.container.setLayout(layout)
        self.container.adjustSize()
        self.w.adjustSize()

    def add_back_button(self, layout: QBoxLayout, function, text="←  Volver Atrás"):
        self.back_button = QPushButton(text)
        self.back_button.clicked.connect(function)
        layout.addWidget(self.back_button)

    def open_file(self, filename):
        # viene de stackoverflow, sirve para abrir el archivo de forma local en el sistema operativo
        if sys.platform == "win32":
            os.startfile(filename)
        else:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, filename])

    def center(self, w):
        frame_gm = w.frameGeometry()
        screen = QApplication.desktop().screenNumber(
            QApplication.desktop().cursor().pos())
        center_point = QApplication.desktop().screenGeometry(screen).center()
        frame_gm.moveCenter(center_point)
        w.move(frame_gm.topLeft())

    window_instance = None

    def get_window(self):
        if Menu.window_instance is None:
            Menu.window_instance = QMainWindow()
            self.center(Menu.window_instance)
        return Menu.window_instance