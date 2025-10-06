from __future__ import annotations
from sys import argv

# Librerías adicionales por si las necesitan
# No son obligatorias y no tampoco tienen que usarlas todas
# No pueden agregar ningun otro import que no esté en esta lista
import os
import typing
import collections
import itertools
import dataclasses
import enum

from Paxos.paxos import Paxos
from Raft.raft import process_raft_file

if __name__ == "__main__":
    # Completar con tu implementación o crea más archivos y funciones
    file = argv[0]  # main.py
    algorithm = argv[1]  # Paxos o Raft
    test_path = argv[2]
    file_name = test_path.split("/")[1].split(".")[0]
    output_path = f"logs/{algorithm}_{file_name}.txt"
    if algorithm == "Paxos":
        paxos = Paxos(test_path)
        paxos.run()
        paxos.save_output(output_path)
    elif algorithm == "Raft":
        process_raft_file(test_path, output_path)