import threading
import socketserver

import functions
import message


class Server(threading.Thread):
    
    allow_reuse_address = True

    def __init__(self, node_id, ip, port):
        threading.Thread.__init__(self)
        self.name = 'Server'
        self.id = node_id
        self.ip = ip
        self.port = int(port)
        self.daemon = True
        self._create_socket()

    def _create_socket(self):
        
        functions.debug_print("Starting server on: "+self.ip+":"+str(self.port))
        socketserver.ThreadingTCPServer.allow_reuse_address = True

        try:
            self.socket = socketserver.ThreadingTCPServer((self.ip, self.port), message.MessageHandler)
        except (OSError, ConnectionRefusedError):
            functions.error_print("Cannot start server, perhaps port is in use.")
        try:
            self.socket.daemon_threads = True
        except AttributeError:
            pass

    def run(self):
       
        try:
            self.socket.serve_forever()
        except AttributeError:
            functions.info_print("Server exiting...")
