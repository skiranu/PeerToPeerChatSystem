from PyQt5 import QtWidgets, uic
import os


def get_dir():
    
    return str(os.path.abspath(os.path.dirname(__file__)))


def load_keys_file(window):
    
    result = QtWidgets.QFileDialog.getOpenFileName(window)
    filepath = result[0]
    if filepath != '':
        window.keys_file = filepath


def gui_main():
    
    directory = get_dir()

    app = QtWidgets.QApplication([])

    window = QtWidgets.QMainWindow()

    with open(directory + '/main.ui') as f:
        uic.loadUi(f, window)
    dialog = QtWidgets.QDialog(window)

    with open(directory + '/startnode.ui') as f:
        uic.loadUi(f, dialog)

    btn = window.findChild(QtWidgets.QPushButton, 'btn_keys')
    btn.clicked.connect(lambda: load_keys_file(window))

    result = dialog.exec()

    if result == QtWidgets.QDialog.Rejected:
        exit(0)
    else:
        ip = dialog.findChild(QtWidgets.QLineEdit, 'ip').text()
        port = dialog.findChild(QtWidgets.QSpinBox, 'port').value()

        ip_next = ip
        port_next = port
        leader = True

        if dialog.findChild(QtWidgets.QCheckBox, 'chck_init').isChecked():
            leader = False
            ip_next = dialog.findChild(QtWidgets.QLineEdit, 'ip_next').text()
            port_next = dialog.findChild(QtWidgets.QSpinBox, 'port_next').value()

        name = dialog.findChild(QtWidgets.QLineEdit, 'name').text()

        if name == "" or name is None:
            QtWidgets.QMessageBox.critical(window, "Error", "You have to specify name of the node.",
                                           QtWidgets.QMessageBox.Close)
            exit(1)
        if ';' in name:
            QtWidgets.QMessageBox.critical(window, "Error", "Sorry your name can't contain character ';'.",
                                           QtWidgets.QMessageBox.Close)
            exit(1)

    window.setWindowTitle("P2P Chat - " + name)

    if hasattr(window, 'keys_file'):
        return [app, window, str(ip), str(port), str(ip_next), str(port_next), leader, name, window.keys_file]
    else:
        return [app, window, str(ip), str(port), str(ip_next), str(port_next), leader, name, None]
