from __future__ import annotations  # Solo lo dejo por si lo necesitan. Lo pueden eliminar
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

# Recuerda que no se permite importar otros módulos/librerías a excepción de los creados
# por ustedes o las ya incluidas en este main.py
from Paxos.paxos import Paxos
from raft import raft

if __name__ == "__main__":
    # Completar con tu implementación o crea más archivos y funciones
    file = argv[0] # main.py
    algorithm = argv[1] # Paxos o Raft
    test_path = argv[2]
    file_name = test_path.split("/")[1].split(".")[0]
    output_path = f"logs/{algorithm}_{file_name}.txt"
    if algorithm == "Paxos":
        paxos = Paxos(test_path)
        paxos.run()
        paxos.save_output(output_path)
    elif algorithm == "Raft":
        raft(test_path)