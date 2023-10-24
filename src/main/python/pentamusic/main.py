from PyQt5.QtWidgets import QApplication
import sys

from pentamusic.menu_manager import MenuManager

# Cargamos la aplicación
app = QApplication(sys.argv)
MenuManager().open_init_menu()
app.exec()
