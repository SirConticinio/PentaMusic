from PyQt5.QtWidgets import QApplication
import sys

from pentamusic.crypto import Crypto
from pentamusic.menu_manager import MenuManager
from pentamusic.menus.dialog import OkDialog

# Cargamos la aplicación
app = QApplication(sys.argv)
MenuManager().open_init_menu()

# Generamos el sistema de carpetas de Crypto
try:
    Crypto.instance.generate_openssl_system()
except Exception as e:
    OkDialog(str(e))

# Y ejecutamos la aplicación
app.exec()