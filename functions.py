from db import save_chat
import time
import pickle
import configparser
import hashlib
import socket

from cryptography.fernet import Fernet
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import Qt

import cnode


def disconnect_from_network():
    
    end_msg = cnode.node.client.create_message(
        'CLOSE',
        cnode.node.ip_next + ":" + cnode.node.port_next
    )
    end_msg['to'] = cnode.node.id
    cnode.node.client.send_data(pickle.dumps(end_msg, -1))

    time.sleep(0.3)

    cnode.node.queue.put(None)

    cnode.node.server.socket.shutdown()
    cnode.node.server.socket.server_close()


def info_print(msg=''):
    
    if cnode.node is not None:
            cnode.node.signal_log_message.emit(msg)


def debug_print(msg=''):
    
    if cnode.node is not None:
            cnode.node.signal_log_message.emit(msg)


def error_print(msg=''):
    
    if cnode.node is not None:
            cnode.node.signal_log_message.emit(msg)


def create_id(ip, port):
    
    return hashlib.sha224((ip + ":" + port).encode('ascii')).hexdigest()


def send_message_from_gui(window):
    
    node_id = window.findChild(QtWidgets.QLineEdit, 'node_id').text()
    msg = window.findChild(QtWidgets.QPlainTextEdit, 'message').toPlainText()
    window.findChild(QtWidgets.QPlainTextEdit, 'message').clear()
    encrypt = window.findChild(QtWidgets.QCheckBox, 'chck_encrypt').isChecked()

    if encrypt:
        try:
            cipher_key = cnode.node.keys[node_id]
        except KeyError:
            QtWidgets.QMessageBox.critical(window, "Missing key.",
                                           "You don't have key for target recipient. "
                                           "Add key in keys.cfg configuration file.",
                                           QtWidgets.QMessageBox.Close)
            return

        cipher = Fernet(cipher_key)
        message = cnode.node.name + ": " + msg
        encrypted_message = cipher.encrypt(message.encode('utf-8'))
        new_msg = cnode.node.client.create_message('MSG', encrypted_message)
        new_msg['encrypted'] = True
    else:
        new_msg = cnode.node.client.create_message(
            'MSG',
            cnode.node.name + ": " + msg
        )

    new_msg['to'] = node_id

    cnode.node.client.send_data(pickle.dumps(new_msg, -1))
    
    recv_messages = cnode.node.window.findChild(QtWidgets.QPlainTextEdit, 'recv_messages')
    recv_messages.appendPlainText(cnode.node.name + ": " + msg)
    if node_id in cnode.node.chat_history:
        cnode.node.chat_history[node_id].append(cnode.node.name + ": " + msg)
        save_chat(cnode.node.name,node_id,msg)
    else:
        cnode.node.chat_history[node_id] = [cnode.node.name + ": " + msg]
        save_chat(cnode.node.name,node_id,msg)

def scan_network_for_users():
    
    scan_message = cnode.node.client.create_message('SCAN', '')
    scan_message['to'] = cnode.node.id

    cnode.node.client.send_data(pickle.dumps(scan_message, -1))


def select_user():
    
    users = cnode.node.window.findChild(QtWidgets.QListWidget, 'users').selectedItems()
    
    if not users:
        return

    users[0].setBackground(QtCore.Qt.white)
    selected_user = None

    for user in users:
        selected_user = user.data(Qt.DisplayRole)

    cnode.node.window.findChild(QtWidgets.QLineEdit, 'node_id').setText(selected_user)
    recv_messages = cnode.node.window.findChild(QtWidgets.QPlainTextEdit, 'recv_messages')

    if selected_user not in cnode.node.chat_history:
        recv_messages.setPlainText("")
        return

    text = cnode.node.chat_history[selected_user]
    text = "\n".join(text)
    
    recv_messages.setPlainText(text)

def read_config(config):
    
    keys_config = configparser.ConfigParser()
    if config is not None:
        try:
            keys_config.read(config)
            return keys_config['keys']
        except KeyError:
            return None
    else:
        return None


@pyqtSlot(str, name='users')
def print_users(users):
    
    list = cnode.node.window.findChild(QtWidgets.QListWidget, 'users')
    list.clear()
    users = sorted(users.split(';'))

    for user in users:
        if user != '':
            list.addItem(QtWidgets.QListWidgetItem(user))


@pyqtSlot(str, name='msg')
def message_received(msg_sender):
    
    list = cnode.node.window.findChild(QtWidgets.QListWidget, 'users')
    user = list.findItems(msg_sender, QtCore.Qt.MatchExactly)
    if user:
        if user[0].isSelected():
            select_user()
        else:
            user[0].setBackground(QtCore.Qt.green)


@pyqtSlot(str, name='log')
def log_received(msg):
    
    recv_messages = cnode.node.window.findChild(QtWidgets.QPlainTextEdit, 'logs')
    recv_messages.appendPlainText(msg)
    

@pyqtSlot(int, name='error')
def missing_key(err_code):
    
    QtWidgets.QMessageBox.critical(cnode.node.window, "Missing key.",
                                   "Someone send you a message encrypted with key you don't have. "
                                   "Add your key in keys.cfg configuration file.",
                                   QtWidgets.QMessageBox.Close)
