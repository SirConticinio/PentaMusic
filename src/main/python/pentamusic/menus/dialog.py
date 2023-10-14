from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QDialogButtonBox, QPushButton, QWidget, QHBoxLayout


class OkDialog(QDialog):
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


class YesNoDialog(QDialog):
    def __init__(self, text, yes_func, no_func):
        super().__init__()
        self.resize(240, 120)
        self.setWindowTitle("PentaMusic")

        # creamos un layout y lo establecemos en el widget
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(QLabel(text))

        group = QWidget()
        group_layout = QHBoxLayout()
        yes = QPushButton("Sí")
        yes.clicked.connect(lambda: self.clicked_button(yes_func))
        no = QPushButton("No")
        no.clicked.connect(lambda: self.clicked_button(no_func))
        group_layout.addWidget(yes)
        group_layout.addWidget(no)
        group.setLayout(group_layout)

        layout.addWidget(group)

        # lo imprimimos y mostramos
        print(text)
        self.show()

    def clicked_button(self, func):
        self.close()
        func()
