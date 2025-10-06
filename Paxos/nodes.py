from typing import List

class AcceptingNode():
    def __init__(self, id):
        self.id = id
        self.isRunning = True # running, stopped
        self.current_term = -1 # mayor prepare(n) recibido
        self.last_accepted_value = None
        self.accepted = []

    def recieve_message(self, type, message):
        if not self.isRunning:
            return None
        if type == "prepare":
            return self.prepare(message["n"])
        elif type == "accept":
            return self.accept(message["n"], message["action"])
        
                    
    def prepare(self, n):
        if self.current_term < n: # ok
            self.current_term = n
            return (True, self.last_accepted_value) 
        
        elif self.current_term > n: # not ok
            return (False, self.last_accepted_value) 

        
    def accept(self, n, action):
        if self.current_term == n:
            self.last_accepted_value = (n, action)
            self.accepted.append((n, action))
        elif self.current_term > n:
            pass # Rechaza la propuesta


class ProposingNode():
    def __init__(self, id):
        self.id = id
        self.current_prepare = -1
        self.isReadyToAccept = False
        self.acceptedAction = None
    
    def send_prepare(self, nodes: List[AcceptingNode], n: int): 
        responses = []
        self.current_prepare = n
        message = {"n": n}
        for node in nodes:
            r = node.recieve_message("prepare", message)
            responses.append(r)
        return responses

    def send_accept(self, nodes: List[AcceptingNode], n: int, action: str):
        responses = []
        self.current_prepare = n
        message = {"n": n, "action": action}
        for node in nodes:
            r = node.recieve_message("accept", message)
            responses.append(r)
        return responses