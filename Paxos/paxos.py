from Paxos.nodes import AcceptingNode, ProposingNode

class Paxos:
    def __init__(self, test_path):
        self.lines = self.read_without_comments(test_path)
        self.accepting_nodes = []
        self.proposing_nodes = []
        self.database = {}
        self.output_lines = []

    def run(self):
        self.create_nodes()
        self.write_output("LOGS")
        for event in self.lines[2:]:
            self.process(event)
        if len(self.output_lines) <= 1:
            self.write_output("No hubo logs")
        # Ahora la bdd
        self.write_output("BASE DE DATOS")
        if not self.database:
            self.write_output("No hay datos")
        else:
            for key in sorted(self.database.keys()):
                self.write_output(f"{key}={self.database[key]}")
        
        


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
            node.acceptedAction = None
            response = node.send_prepare(self.accepting_nodes, n)

        not_null_responses = [r for r in response if r is not None]
        if not_null_responses:
            ok_count = sum(1 for r in response if r[0])
            if ok_count > len(self.accepting_nodes) / 2:
                node.accepted_n = n

    def accept(self, node_id, n, action):
        node = next((node for node in self.proposing_nodes if node.id == node_id), None)
        response = []
        if node.acceptedAction:
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
        all_actions = set()
        for node in self.accepting_nodes:
            for term_action in node.accepted:
                all_actions.add(term_action)

        # Consolidar solo las acciones que están en la mayoría de los nodos
        for term_action in sorted(all_actions, key=lambda x: (x[0], x[1])):
            count = sum(1 for node in self.accepting_nodes if term_action in node.accepted)
            if count > len(self.accepting_nodes) / 2:
                self.insert_db(term_action[1])
        self.reset()

    def write_output(self, line):
        self.output_lines.append(line)
        
    def reset(self):
        #TODO Mover esta lógica al nodo mismo, que debería recibir un mensaje de reset
        for node in self.proposing_nodes:
            node.current_prepare = -1
            node.accepted_n = None
            node.acceptedAction = None
        for node in self.accepting_nodes:
            if not node.isRunning:
                continue
            node.current_term = -1
            node.accepted = []
            node.last_accepted_value = None

    def log(self, var):
        value = self.database.get(var, "Variable no existe")
        self.write_output(f"{var}={value}")

    def save_output(self, filename="paxos_output.txt"):
        with open(filename, 'w') as f:
            for line in self.output_lines:
                f.write(line + "\n")

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

