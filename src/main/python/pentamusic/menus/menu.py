import os
import shutil
import subprocess
import sys
import tempfile
import uuid

from PyQt5.QtWidgets import QMainWindow, QWidget, QPushButton, QBoxLayout, QApplication

from pentamusic.basedatos.session import Session
from pentamusic.basedatos.sql import SQL
from pentamusic.crypto import Crypto
from pentamusic.menu_manager import MenuManager
from pentamusic.menus.dialog import OkDialog


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
        self.session = Session()

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

    def save_sheet(self, filename, should_encrypt, should_decrypt, open_edit_menu, original_id, decrypt_nonce=b""):
        home = os.path.expanduser("~/PentaMusic/Sheets")
        file_nonce = b""
        if not os.path.exists(home):
            os.makedirs(home)

        # la copiamos primero a un archivo temporal
        temp = tempfile.NamedTemporaryFile()
        with open(filename, mode="rb") as encrypted_sheet:
            contents = encrypted_sheet.read()
            if should_decrypt:
                contents = Crypto().decrypt_data(contents, decrypt_nonce, False)
            if should_encrypt:
                file_nonce = os.urandom(12)
                contents = Crypto().encrypt_data(contents, file_nonce)
            temp.write(contents)

        # y lo guardamos con un nombre random, pero en la base de datos se guarda el original
        originalname = os.path.basename(filename).removesuffix(".pdf")
        my_id = original_id if not original_id == "" else str(uuid.uuid4())
        path = home + "/" + my_id + ".pdf"
        shutil.copy2(temp.name, path)
        temp.close()

        # lo guardamos en la tabla
        try:
            if original_id == "":
                self.datos.insert_sheet(my_id, originalname, self.session.user, False, file_nonce, "", "")
            else:
                sheet = self.datos.get_sheet(my_id)
                self.datos.update_sheet(my_id, sheet.title, sheet.owner, sheet.is_public, file_nonce, sheet.composer, sheet.instrument)
        except Exception as e:
            OkDialog("Hubo un error al guardar el archivo:\n" + str(e))

        # y ahora abrimos el menú de edición
        if open_edit_menu:
            self.manager.open_usersheet_edit_menu(my_id)

    def get_sheet_path(self, sheet_id) -> str:
        return os.path.expanduser("~/PentaMusic/Sheets/" + sheet_id + ".pdf")

    def open_sheet(self, sheet):
        sheet_id = sheet.sheet_id
        nonce = sheet.file_nonce
        is_encrypted = sheet.is_encrypted()
        filename = self.get_sheet_path(sheet_id)

        # Tenemos que comprobar si la partitura es privada, en ese caso tenemos que desencriptarla
        if is_encrypted:
            file = tempfile.NamedTemporaryFile(delete=False)
            with open(filename, mode="rb") as encrypted_sheet:
                contents = encrypted_sheet.read()
                decrypted = Crypto().decrypt_data(contents, nonce, False)
                file.write(decrypted)
                filename = file.name

        # Ahora abrimos el archivo como tal
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