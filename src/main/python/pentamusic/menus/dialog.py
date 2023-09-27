from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QDialogButtonBox, QPushButton


class Dialog(QDialog):
    def __init__(self, text):
        super().__init__()
        self.resize(240, 120)
        self.setWindowTitle("PentaMusic")

        # creamos un layout y lo establecemos en el widget
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(QLabel(text))
        ok = QPushButton("OK")
        ok.clicked.connect(lambda: self.close())
        layout.addWidget(ok)

        # lo imprimimos y mostramos
        print(text)
        self.show()
