import sys
import os

class Node:
    def __init__(self, node_id, election_timeout):
        self.node_id = node_id
        self.election_timeout = election_timeout
        self.log = []  # (term, action)
        self.is_active = True
        self.term = 0

    def stop(self):
        self.is_active = False

    def start(self):
        self.is_active = True

class RaftSimulator:
    def __init__(self, nodes_str):
        self.nodes = {}
        self.leader = None
        self.database = {}
        self.logs_output = []
        self.current_term = 0
        self.commit_index = -1
        self.last_applied = -1
        self.majority = 0

        # crate nodes
        if '#' in nodes_str:
            nodes_str = nodes_str.split('#')[0].strip()
        node_definitions = [n.strip() for n in nodes_str.split(';') if n.strip()]

        for node_def in node_definitions:
            parts = [p.strip() for p in node_def.split(',')]
            node_id = parts[0]
            timeout = int(parts[1])
            self.nodes[node_id] = Node(node_id, timeout)

        self.majority = (len(self.nodes) // 2) + 1

        # select leader
        self.elect_leader()
        if self.leader:
            for node in self.nodes.values():
                node.term = self.current_term

    def elect_leader(self):
        active_nodes = [node for node in self.nodes.values() if node.is_active]
        if len(active_nodes) < self.majority:
            self.leader = None
            return
        
        active_nodes.sort(key=lambda n: n.election_timeout)

        # vote
        for candidate in active_nodes:
            candidate_last_term = candidate.log[-1][0] if candidate.log else 0
            candidate_len = len(candidate.log)
            vote_count = 0
            for voter in active_nodes:
                voter_last_term = voter.log[-1][0] if voter.log else 0
                voter_len = len(voter.log)
                if candidate_last_term > voter_last_term or (
                    candidate_last_term == voter_last_term and candidate_len >= voter_len
                    ):
                    vote_count += 1
            # wins vote 
            if vote_count >= self.majority:
                self.leader = candidate.node_id
                self.current_term += 1
                candidate.term = self.current_term

                for node in active_nodes:
                    node.term = self.current_term
                self.commit()
                return

        self.leader = None

    def update_commit_index(self): 
        if not self.leader:
            return

        leader_node = self.nodes[self.leader]
        for i in range(len(leader_node.log) - 1, self.commit_index, -1):
            if leader_node.log[i][0] != leader_node.term:
                continue

            count = 0
            for node in self.nodes.values():
                if len(node.log) > i and node.log[:i + 1] == leader_node.log[:i + 1]:
                    count += 1
            if count >= self.majority:
                self.commit_index = i
                break

    def apply_committed(self):
        while self.commit_index > self.last_applied:
            self.last_applied += 1
            action = self.nodes[self.leader].log[self.last_applied][1]
            self.process_action(action)

    def commit(self): # (consolidacion)
        self.update_commit_index()
        self.apply_committed()

    def process_action(self, action):
        parts = action.split('-', 2)
        command = parts[0]
        variable = parts[1]
        value = parts[2] if len(parts) > 2 else ""

        if command == 'SET':
            self.database[variable] = value

        elif command == 'ADD':
            if variable not in self.database:
                self.database[variable] = value
            else:
                current = self.database[variable]
                if current.isdigit() and value.isdigit():
                    self.database[variable] = str(int(current) + int(value))
                else:
                    self.database[variable] = current + value

        elif command == 'DEL':
            if variable in self.database:
                del self.database[variable]

    def process_event(self, event):
        parts = event.split(';', 1)
        command = parts[0].strip()
        args = parts[1].strip() if len(parts) > 1 else ""

        if command == 'Send':
            if self.leader:
                leader_node = self.nodes.get(self.leader)
                if leader_node and leader_node.is_active:
                    leader_node.log.append((leader_node.term, args))
                    self.commit()

        elif command == 'Spread':
            if not self.leader:
                return
            leader_node = self.nodes[self.leader]
            if not leader_node.is_active:
                return
            node_list_str = args.strip('[]')
            target_ids = [n.strip() for n in node_list_str.split(',')] if node_list_str else []
            for target_id in target_ids:
                if target_id in self.nodes:
                    target_node = self.nodes[target_id]
                    if target_node.is_active:
                        target_node.log = leader_node.log.copy()
            self.commit()

        elif command == 'Stop':
            if args in self.nodes:
                self.nodes[args].stop()
                if args == self.leader:
                    self.leader = None
                    self.elect_leader()
                self.commit()

        elif command == 'Start':
            if args in self.nodes:
                node = self.nodes[args]
                node.start()
                if self.leader:
                    node.term = self.nodes[self.leader].term
                self.commit()
                if self.leader is None:
                    self.elect_leader()

        elif command == 'Log':
            if args in self.database:
                self.logs_output.append(f"{args}={self.database[args]}")
            else:
                self.logs_output.append(f"{args}=Variable no existe")

    def generate_output(self):
        output = ["LOGS"]
        if self.logs_output:
            output += self.logs_output
        else:
            output.append("No hubo logs")
        output.append("BASE DE DATOS")
        if self.database:
            for var in sorted(self.database):
                output.append(f"{var}={self.database[var]}")
        else:
            output.append("No hay datos")
        return "\n".join(output)

def process_raft_file(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines()]

    # nodes
    nodes_str = lines[0]
    simulator = RaftSimulator(nodes_str)

    # events
    for line in lines[1:]:
        if line and not line.startswith('#'):
            if '#' in line:
                line = line.split('#')[0].strip()
            if line:
                simulator.process_event(line)

    # output
    output_content = simulator.generate_output()
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output_content)

if __name__ == "__main__":
    
    input_path = "test_input.txt"
    output_path = "test_output.txt"
    process_raft_file(input_path, output_path)

# Se utilizo IA para la idea del uso de las variables commit_index