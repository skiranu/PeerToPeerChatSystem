import socketserver
import pickle

import cnode
import functions


class MessageHandler(socketserver.BaseRequestHandler):
    
    def handle(self):
        
        data = self.request.recv(4096)
        if len(data) == 0:
            return

        message = pickle.loads(data)

        if message['state'] == 'DIE':
            functions.info_print("RECEIVED DIE")
            return
        
        elif message['state'] == 'PING':
        
            functions.debug_print("RECEIVED PING MESSAGE from: " + message['from'])
            cnode.node.ping_queue.put(message)
        
        else:
            cnode.node.queue.put(message)
