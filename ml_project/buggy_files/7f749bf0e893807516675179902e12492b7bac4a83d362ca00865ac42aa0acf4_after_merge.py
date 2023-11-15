def die_program(n):
    """
    Generate a quantum program to roll a die of n faces.
    """
    prog = pq.Program()
    ro = prog.declare('ro')
    qubits = qubits_needed(n)
    # Hadamard initialize.
    for q in range(qubits):
        prog.inst(H(q))
    # Measure everything.
    for q in range(qubits):
        prog.measure(q, ro[q])
    return prog