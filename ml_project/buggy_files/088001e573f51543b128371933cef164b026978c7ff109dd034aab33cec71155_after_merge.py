def meyer_penny_program():
    """
    Returns the program to simulate the Meyer-Penny Game
    The full description is available in docs/source/examples.rst

    :return: pyQuil Program
    """
    prog = pq.Program()
    ro = prog.declare('ro')
    picard_register = ro[1]
    answer_register = ro[0]

    then_branch = pq.Program(X(0))
    else_branch = pq.Program(I(0))

    # Prepare Qubits in Heads state or superposition, respectively
    prog.inst(X(0), H(1))
    # Q puts the coin into a superposition
    prog.inst(H(0))
    # Picard makes a decision and acts accordingly
    prog.measure(1, picard_register)
    prog.if_then(picard_register, then_branch, else_branch)
    # Q undoes his superposition operation
    prog.inst(H(0))
    # The outcome is recorded into the answer register
    prog.measure(0, answer_register)

    return prog