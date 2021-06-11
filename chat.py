import hashlib
import logging

from PyQt5 import QtWidgets

import cnode
import functions
from cnode import Node
from gui import gui_main
import main

def gui():
    

    [app, window, ip, port, ip_next, port_next, leader, name, keys_file] = gui_main()
    node_id = functions.create_id(ip, port)
    cnode.node = Node(node_id, ip, ip_next, port, port_next, name, window)

    if leader:
        cnode.node.state = 'ALONE'
        cnode.node.leader = True
        cnode.node.leader_id = node_id

    cnode.node.keys = functions.read_config(keys_file)
    if cnode.node.keys is None:
        window.findChild(QtWidgets.QCheckBox, 'chck_encrypt').setEnabled(False)

    try:
        cnode.node.start()
    except (OSError, ConnectionRefusedError):
        functions.error_print("Error while starting node.")
        exit(1)

    btn = window.findChild(QtWidgets.QPushButton, 'button_send')
    btn.clicked.connect(lambda: functions.send_message_from_gui(window))

    btn_scan = window.findChild(QtWidgets.QPushButton, 'btn_scan')
    btn_scan.clicked.connect(lambda: functions.scan_network_for_users())

    user_list = cnode.node.window.findChild(QtWidgets.QListWidget, 'users')
    user_list.itemSelectionChanged.connect(functions.select_user)

    cnode.node.signal_message.connect(functions.message_received)
    cnode.node.signal_log_message.connect(functions.log_received)
    cnode.node.signal_error.connect(functions.missing_key)
    cnode.node.signal_scan.connect(functions.print_users)

    window.show()
    ret_code = app.exec()
    functions.disconnect_from_network()
    return ret_code

def main():
    gui()


if __name__ == '__main__':
    main()
