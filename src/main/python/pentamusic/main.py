from PyQt5.QtWidgets import QApplication, QMainWindow
from menus.init_menu import InitWindow


# Only needed for access to command line arguments
import sys

# You need one (and only one) QApplication instance per application.
# Pass in sys.argv to allow command line arguments for your app.
# If you know you won't use command line arguments QApplication([]) works too.
app = QApplication(sys.argv)

# Create a Qt widget, which will be our window.
window = InitWindow()

# Start the event loop.
app.exec()


# Your application won't reach here until you exit and the event
# loop has stopped.