def meyer_penny_program():
    """
    Returns the program to simulate the Meyer-Penny Game
    The full description is available in docs/source/examples.rst

    :return: pyQuil Program
    """

    picard_register = 1
    answer_register = 0

    then_branch = pq.Program(X(0))
    else_branch = pq.Program(I(0))

    return (pq.Program()
            # Prepare Qubits in Heads state or superposition, respectively
            .inst(X(0), H(1))
            # Q puts the coin into a superposition
            .inst(H(0))
            # Picard makes a decision and acts accordingly
            .measure(1, picard_register)
            .if_then(picard_register, then_branch, else_branch)
            # Q undoes his superposition operation
            .inst(H(0))
            # The outcome is recorded into the answer register
            .measure(0, answer_register))