class AcceptingNode():
    def __init__(self, id):
        self.id = id
        self.state = 'running' # running, stopped
        self.current_term = -1 # mayor prepare(n) recibido
        self.voted_for = None
        self.last_accepted_n = None
        self.last_accepted_value = None

    def recieve_message(self, message):
        if self.state == 'stopped':
            return None
        # Procesar mensaje
                    
    def prepare(self, n):
        if self.current_term == -1: # ok
            self.current_term = n
            return (True, self.last_accepted_n, self.last_accepted_value) 
        
        elif self.current_term > n: # not ok
            return (False, self.last_accepted_n, self.last_accepted_value) 
        
        elif self.current_term < n:
            self.current_term = n # promete no aceptar nada menor a n
            return (True, self.last_accepted_n, self.last_accepted_value)  


class ProposingNode():
    def __init__(self, id):
        self.id = id
        self.current_prepare = -1
        self.current_accept = None
    
    def send_prepare(self, nodes, n):
        response = []
        for node in nodes:
            response.append(node.prepare(n))
        return response

class Paxos:
    def __init__(self, test_path):
        self.lines = self.read_without_comments(test_path)
        self.accepting_nodes = []
        self.proposing_nodes = []

    def run(self):
        self.create_nodes()
        for event in self.lines[2:]:
            self.process(event)

    def process(self, event):
        instruction = event.split(";")[0]
        
        if instruction == "Prepare":
            proposing_node = event.split(";")[1]
            term = event.split(";")[2]
            self.prepare(proposing_node, term)
        elif instruction == "Accept":
            print("Accept Not implemented ")
        elif instruction == "Stop":
            pass
        elif instruction == "Start":
            pass
        elif instruction == "Learn":
            pass
        elif instruction == "Log":
            pass
        else:
            raise ValueError("Instrucción Desconocida")
        
    def prepare(self, node_id, n):
        node = next((node for node in self.proposing_nodes if node.id == node_id), None)
        response = []
        if node:
            response = node.send_prepare(self.accepting_nodes, n)
            print("response es", response)
        ok_count = sum(1 for r in response if r[0])
        majority = ok_count > len(self.accepting_nodes) / 2
        
        

    def create_nodes(self):
        for node_id in self.lines[0].split(";"):
            new_node = AcceptingNode(node_id)
            self.accepting_nodes.append(new_node)
        for node_id in self.lines[1].split(";"):
            new_node = ProposingNode(node_id)
            self.proposing_nodes.append(new_node)

    def read_without_comments(self, test_path):
        clean_lines = []
        with open(test_path, 'r') as f:
            for line in f:
                stripped_line = line.strip()

                if stripped_line.startswith('#'):
                    continue

                if '#' in stripped_line:
                    line_before_comment = stripped_line.split('#', 1)[0].strip()
                    if line_before_comment: # La línea no estaba vacía antes 
                        clean_lines.append(line_before_comment)
                else:
                    if stripped_line: # Lineas comunes sin comentarios
                        clean_lines.append(stripped_line)
        return clean_lines

