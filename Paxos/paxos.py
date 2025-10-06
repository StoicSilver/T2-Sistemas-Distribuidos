from Paxos.nodes import AcceptingNode, ProposingNode

class Paxos:
    def __init__(self, test_path):
        self.lines = self.read_without_comments(test_path)
        self.accepting_nodes = []
        self.proposing_nodes = []
        self.database = {}

    def run(self):
        self.create_nodes()
        for event in self.lines[2:]:
            self.process(event)

    def process(self, event):
        instruction = event.split(";")[0]
        
        if instruction == "Prepare":
            proposing_node = event.split(";")[1]
            term = int(event.split(";")[2])
            self.prepare(proposing_node, term)
        elif instruction == "Accept":
            proposing_node = event.split(";")[1]
            term = int(event.split(";")[2])
            action = event.split(";")[3]
            self.accept(proposing_node, term, action)
        elif instruction == "Stop":
            node_id = event.split(";")[1]
            self.stop(node_id)
        elif instruction == "Start":
            node_id = event.split(";")[1]
            self.start(node_id)
        elif instruction == "Learn":
            self.learn()
        elif instruction == "Log":
            var = event.split(";")[1]
            self.log(var)
        else:
            raise ValueError("Instrucción Desconocida")
        
    def prepare(self, node_id, n):
        node = next((node for node in self.proposing_nodes if node.id == node_id), None)
        response = []
        if node:
            response = node.send_prepare(self.accepting_nodes, n)

        not_null_responses = [r for r in response if r is not None]
        if not not_null_responses:
            ok_count = sum(1 for r in response if r[0])
            node.isReadyToAccept = ok_count > len(self.accepting_nodes) / 2
            # Busca la acción con el n más alto entre las responses
            accepted_responses = [r[1] for r in response if r[1] is not None]
            if node.isReadyToAccept and accepted_responses:
                self.acceptedAction = max(accepted_responses, key=lambda x: x[0])
            else:
                self.acceptedAction = None

    def accept(self, node_id, n, action):
        node = next((node for node in self.proposing_nodes if node.id == node_id), None)
        response = []
        if node.acceptedAction:
            n = node.acceptedAction[0]
            action = node.acceptedAction[1]
        if node:
            response = node.send_accept(self.accepting_nodes, n, action)

    def stop(self, node_id): 
        node = next((node for node in self.accepting_nodes if node.id == node_id), None)
        if node:
            node.isRunning = False
    
    def start(self, node_id):
        node = next((node for node in self.accepting_nodes if node.id == node_id), None)
        if node:
            node.isRunning = True

    def learn(self):
        for node in self.accepting_nodes:
            for term_action in node.accepted:
                count = sum(1 for n in self.accepting_nodes if term_action in n.accepted)
                if count > len(self.accepting_nodes) / 2:
                    self.insert_db(term_action[1])

        self.reset()

    def reset(self):
        #TODO Mover esta lógica al nodo mismo, que debería recibir un mensaje de reset
        for node in self.proposing_nodes:
            node.isReadyToAccept = False
            node.current_prepare = -1
        for node in self.accepting_nodes:
            node.current_term = -1
            node.accepted = []

    def log(self, var):
        value = self.database.get(var, "Variable no existe")
        print(f"Log {var}: {value}")

    def insert_db(self, action):
        """COMANDO-VARIABLE-VALOR"""
        command = action.split("-")[0]
        variable = action.split("-")[1]
        value = action.split("-")[2]
        if command == "SET":
            self.database[variable] = value
        elif command == "ADD":
            # suma valor a variable en la base de datos si existe.
            if variable in self.database:
                if self.database[variable].isdigit() and value.isdigit():
                    self.database[variable] = self.database[variable] + value
                else:
                    self.database[variable] = str(self.database[variable]) + str(value)
            else:
                self.database[variable] = value
        elif command == "DEL":
            # borra variable de la base de datos si existe
            if variable in self.database:
                del self.database[variable]



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

