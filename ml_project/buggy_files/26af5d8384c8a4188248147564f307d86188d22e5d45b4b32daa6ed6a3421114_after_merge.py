def teleport(start_index, end_index, ancilla_index):
    """Teleport a qubit from start to end using an ancilla qubit
    """
    program = make_bell_pair(end_index, ancilla_index)

    ro = program.declare('ro')

    # do the teleportation
    program.inst(CNOT(start_index, ancilla_index))
    program.inst(H(start_index))

    # measure the results and store them in classical registers [0] and [1]
    program.measure(start_index, ro[0])
    program.measure(ancilla_index, ro[1])

    program.if_then(ro[1], X(2))
    program.if_then(ro[0], Z(2))

    program.measure(end_index, ro[2])

    print(program)
    return program