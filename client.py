import threading
import socket
import time
import pickle
import sys

from cryptography.fernet import Fernet

import cnode
import functions



class Client(threading.Thread):
    
    def __init__(self, node_id, state, body):
        threading.Thread.__init__(self)
        self.name = 'Client'
        self.daemon = True
        self.state = state
        self.body = body
        self.id = node_id
        self.socket = None

    def create_socket(self):
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((cnode.node.ip_next, int(cnode.node.port_next)))

    def close_socket(self):
        
        self.socket.close()

    def send_data(self, data):
        
        self.create_socket()
        self.socket.sendall(data)

    def create_message(self, state, body):
        
        if state == 'PING':
            message = {
                'from': cnode.node.ip + ":" + cnode.node.port,
                'to': cnode.node.ip_next + ":" + cnode.node.port_next,
                'state':  state,
                'body': body,
                'at_leader': False,
                'clock': cnode.node.clock,
                'encrypted': False
            }
        else:
            message = {
                'from': cnode.node.ip + ":" + cnode.node.port,
                'to': cnode.node.ip_next + ":" + cnode.node.port_next,
                'state':  state,
                'body': body,
                'at_leader': False,
                'clock': cnode.node.increment_clock(),
                'encrypted': False
            }

        return message

    def run(self):
        
        time.sleep(0.5)

        message = self.create_message(self.state, self.body)
        try:
            self.send_data(pickle.dumps(message, -1))
        except (OSError, ConnectionRefusedError):
            functions.error_print("Cant connect to target node, perhaps target node is not running.")
            return

        while True:
            message = cnode.node.queue.get()
            end = self.do_task(message)
            cnode.node.queue.task_done()

            if end:
                self.close_socket()
                return

    def display_message(self, msg, encrypted=False):
        
        if encrypted:
            try:
                cipher_key = cnode.node.keys[cnode.node.name]
                cipher = Fernet(cipher_key)
                msg = (cipher.decrypt(msg)).decode('utf-8')
                print(msg)
            except KeyError:
                cnode.node.signal_error.emit(1)
                return
        
        msg_sender = msg.split(':')[0]
        print(msg_sender)
        if msg_sender in cnode.node.chat_history:
            cnode.node.chat_history[msg_sender].append(msg)
        else:
            cnode.node.chat_history[msg_sender] = [msg]
        
        cnode.node.signal_message.emit(msg_sender)

    def initiate_voting(self):
        
        cnode.node.voting = True

        voting_message = self.create_message('ELECTION', '')
        voting_message['from'] = cnode.node.id
        self.send_data(pickle.dumps(voting_message, -1))

    def do_task(self, message):
        
        if message is None:
            functions.info_print("EXITING client")
            return True

        cnode.node.set_clock(message['clock'])

        if message['state'] == 'CONNECTING':
            if message['from'] != message['to']:
                ip, port = message['from'].split(":")

                if cnode.node.state == 'ALONE':
                    answer = cnode.node.client.create_message('SET', 'ALONE')
                else:
                    answer = cnode.node.client.create_message('SET', '')
                    answer['to'] = cnode.node.ip_next + ":" + cnode.node.port_next
                cnode.node.state = 'CONNECTED'

                cnode.node.ip_next = ip
                cnode.node.port_next = port

                self.send_data(pickle.dumps(answer, -1))
            
            else:
                functions.debug_print('Connected to itself')

        elif message['state'] == 'SET':
            functions.debug_print("Setting next node...")

            if message['body'] == 'ALONE':
                ip, port = message['from'].split(":")
            else:
                ip, port = message['to'].split(":")

            cnode.node.ip_next = ip
            cnode.node.port_next = port

            cnode.node.state = 'CONNECTED'
            answer = cnode.node.client.create_message('DONE', '')
            self.send_data(pickle.dumps(answer, -1))

        elif message['state'] == 'DONE':
            self.initiate_voting()

            functions.debug_print("Connection established...")
            functions.debug_print("Initiate voting new leader")

        elif message['state'] == 'MSG':

            if cnode.node.leader:
                if message['to'] == cnode.node.id \
                        or message['to'] == cnode.node.name:
                    if message['encrypted']:
                        self.display_message(message['body'], True)
                    else:
                        self.display_message(message['body'])
                elif message['at_leader']:
                    functions.debug_print("NONEXISTENT USER, destroying message...")
                else:
                    if (message['to'] == None or message['to'] == "")\
                         and (message['from'] != cnode.node.ip + ":" + cnode.node.port):
                        if message['encrypted']:
                            self.display_message(message['body'], True)
                        else:
                            self.display_message(message['body'])
                    message['at_leader'] = True
                    self.send_data(pickle.dumps(message, -1))
            else:
                if (message['to'] == cnode.node.id
                    or message['to'] == cnode.node.name)\
                        and message['at_leader']:
                    if message['encrypted']:
                        self.display_message(message['body'], True)
                    else:
                        self.display_message(message['body'])
                elif (message['to'] == None or message['to'] == "")\
                    and (message['from'] != cnode.node.ip + ":" + cnode.node.port)\
                    and message['at_leader']:
                    if message['encrypted']:
                        self.display_message(message['body'], True)
                    else:
                        self.display_message(message['body'])
                    self.send_data(pickle.dumps(message, -1))
                else:
                    self.send_data(pickle.dumps(message, -1))

        elif message['state'] == 'CLOSE':
            functions.debug_print("RECEIVED CLOSING MESSAGE")
            next_id = functions.create_id(
                cnode.node.ip_next,
                cnode.node.port_next
            )

            if message['to'] == cnode.node.id:
                die_msg = self.create_message('DIE', '')
                self.send_data(pickle.dumps(die_msg, -1))

            elif message['to'] == next_id:
                ip_port = message['body']
                ip, port = ip_port.split(":")
                die_msg = self.create_message('DIE', '')

                try:
                    self.send_data(pickle.dumps(die_msg, -1))
                except (OSError,ConnectionRefusedError):
                    pass

                cnode.node.ip_next = ip
                cnode.node.port_next = port

                self.initiate_voting()

            else:
                self.send_data(pickle.dumps(message, -1))

        elif message['state'] == 'WHO_IS_DEAD':
            try:
                self.send_data(pickle.dumps(message, -1))
            except (OSError, ConnectionRefusedError):
                ip_port = message['body']
                ip, port = ip_port.split(":")
                cnode.node.ip_next = ip
                cnode.node.port_next = port

                functions.error_print("I found dead node, trying to repair connection.")
                msg = self.create_message('REPAIRED', '')
                self.send_data(pickle.dumps(msg, -1))

        elif message['state'] == 'REPAIRED':
            functions.debug_print('Connection repaired.')
            functions.debug_print('Initiate voting new leader.')
            self.initiate_voting()

        elif message['state'] == 'SCAN':
            if message['to'] == cnode.node.id:
                cnode.node.signal_scan.emit(message['body'])
            else:
                users = message['body']
                users += cnode.node.name + ";"
                message['body'] = users
                self.send_data(pickle.dumps(message, -1))

        elif message['state'] == 'ELECTION':
            if int(message['from'], 16) > int(cnode.node.id, 16):
                cnode.node.voting = True
                self.send_data(pickle.dumps(message, -1))
           
            if (int(message['from'], 16) < int(cnode.node.id, 16)) \
                    and not cnode.node.voting:
                voting_message = self.create_message('ELECTION', '')
                voting_message['from'] = cnode.node.id
                self.send_data(pickle.dumps(voting_message, -1))
                cnode.node.voting = True

            if int(message['from'], 16) == int(cnode.node.id, 16):
                elected_message = self.create_message('ELECTED', '')
                elected_message['from'] = cnode.node.id
                self.send_data(pickle.dumps(elected_message, -1))
        
        elif message['state'] == 'ELECTED':
            cnode.node.leader_id = message['from']
            cnode.node.voting = False
            cnode.node.leader = True

            functions.debug_print("NEW LEADER IS " + cnode.node.leader_id)

            if cnode.node.id != message['from']:
                cnode.node.leader = False
                self.send_data(pickle.dumps(message, -1))

        else:
            functions.debug_print("UNKNOWN MESSAGE: ")
            functions.debug_print(str(message))

        cnode.node.debug(message)
        return False
