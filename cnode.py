import threading
from queue import Queue
from PyQt5.QtCore import pyqtSignal, QObject
from db import retrieve_chat
import functions
from server import Server
from pinger import Pinger
from client import Client


class Node(QObject):
    
    signal_message = pyqtSignal(str,  name='msg')
    signal_log_message = pyqtSignal(str,  name='log')
    signal_error = pyqtSignal(int, name='error')
    signal_scan = pyqtSignal(str, name='users')

    def __init__(self, node_id, ip, ip_next, port, port_next, name, window=None):
        QObject.__init__(self)
        self.id = node_id
        self.state = 'DISCONNECTED'
        self.ip = ip
        self.ip_next = ip_next
        self.port = port
        self.port_next = port_next
        self.queue = Queue()
        self.ping_queue = Queue()
        self.name = name
        self.leader = False
        self.leader_id = 0
        self.voting = False
        self.clock = 0
        self.server = Server(id, ip, port)
        self.client = Client(id, 'CONNECTING', '')
        self.pinger = Pinger()
        self.window = window
        self.keys = None
        self.chat_history = {}
        

    def debug(self, message):
        
        functions.debug_print("***************")
        functions.debug_print("Timestamp: " + str(self.clock))
        functions.debug_print("ID: " + str(self.id))
        functions.debug_print("Name: " + self.name)
        functions.debug_print("Status: " + self.state)
        functions.debug_print("Leader: " + str(self.leader))
        functions.debug_print("Leader ID: " + str(self.leader_id))
        functions.debug_print("IP:port: " + self.ip + ":" + self.port)
        functions.debug_print("IP_next:port_next: " + self.ip_next + ":" + self.port_next)
        functions.debug_print("Message: ")
        functions.debug_print(str(message))
        functions.debug_print("***************")

    def increment_clock(self):
        
        mutex = threading.Lock()
        with mutex:
            self.clock += 1
        return self.clock

    def set_clock(self, other_clock):
        
        mutex = threading.Lock()
        with mutex:
            self.clock = max(self.clock, other_clock) + 1

    def start(self):
        
        self.server.start()
        self.client.start()
        self.pinger.start()

        chats = retrieve_chat(self.name)
        

        for data in chats:
            if data['receiver'] != self.name:
                if data['receiver'] not in self.chat_history:
                    self.chat_history[data['receiver']] = [data['sender'] + ': ' + data['text']]
                else:
                    self.chat_history[data['receiver']].append(data['sender'] + ': ' + data['text'])

            else:
                if data['sender'] not in self.chat_history:
                    self.chat_history[data['sender']] = [data['sender'] + ': ' + data['text']]
                else:
                    self.chat_history[data['sender']].append(data['sender'] + ': ' + data['text'])
        

node = None