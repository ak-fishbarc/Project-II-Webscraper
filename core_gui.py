import sys
from PyQt5 import QtWidgets as qw

import core_scrape as cscrp


class App(qw.QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'Training Manager'
        self.resize(500, 500)

        self.setWindowTitle(self.title)

        self.form_box = qw.QFormLayout()
        self.set_form()
        self.show()

    def set_form(self):
        login_button = qw.QPushButton('Login')
        login_button.clicked.connect(self.login_pressed)
        login_button.setFixedSize(75, 25)

        username_box = qw.QLineEdit(self)
        username_box.setFixedSize(125, 25)

        password_box = qw.QLineEdit(self)
        password_box.setFixedSize(125, 25)
        password_box.setEchoMode(qw.QLineEdit.Password)

        self.form_box.addRow(qw.QLabel('Username'), username_box)
        self.form_box.addRow(qw.QLabel('Password'), password_box)
        self.form_box.addWidget(login_button)
        self.setLayout(self.form_box)

    def login_pressed(self):
        username = self.username_box.text()
        password = self.password_box.text()
        cscrp.scrape_data(username, password)


if __name__ == "__main__":
    app = qw.QApplication([])
    start_app = App()
    sys.exit(app.exec_())
