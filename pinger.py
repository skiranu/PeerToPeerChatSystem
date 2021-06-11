import threading
import time
import pickle
import cnode
import functions



class Pinger(threading.Thread):
   
    def __init__(self):
        threading.Thread.__init__(self)
        self.interval = 2
        self.errors = 0
        self.attempts = 2
        self.daemon = True

    def run(self):
        
        time.sleep(1)

        while True:
            p = cnode.node.client.create_message('PING', '')

            try:
                cnode.node.client.send_data(pickle.dumps(p, -1))
            except (OSError, ConnectionRefusedError):
                pass

            time.sleep(self.interval)

            if self.errors > self.attempts:
                functions.error_print("NODE BEHIND ME IS DEAD")
                dead_message = cnode.node.client.create_message('WHO_IS_DEAD', cnode.node.ip + ":" + cnode.node.port)
                try:
                    cnode.node.client.send_data(pickle.dumps(dead_message, -1))
                except (OSError, ConnectionRefusedError):
                    cnode.node.queue.put(dead_message)
                self.errors = 0

            elif cnode.node.ping_queue.qsize() > 0:
                self.errors = 0
                cnode.node.ping_queue.get()
                cnode.node.ping_queue.task_done()
            
            else:
                self.errors += 1
