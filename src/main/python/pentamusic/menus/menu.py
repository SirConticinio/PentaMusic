from PyQt5.QtWidgets import QMainWindow, QWidget
from pentamusic.basedatos.sql import SQL
from pentamusic.crypto import Crypto


class Menu:
    def __init__(self, is_separate_window = False):
        if not is_separate_window:
            self.w = self.get_window()
        else:
            self.w = QMainWindow()

        self.setup_window()
        self.datos = SQL()
        self.crypto = Crypto()
        self.w.show()

    def setup_window(self):
        self.w.setWindowTitle("PentaMusic")
        if self.w.centralWidget() is not None:
            self.w.centralWidget().destroy()

        # Set the central widget of the Window.
        self.container = QWidget()
        self.w.setCentralWidget(self.container)

    window_instance = None

    def get_window(self):
        if Menu.window_instance is None:
            Menu.window_instance = QMainWindow()
        return Menu.window_instance

