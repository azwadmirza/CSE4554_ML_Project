def body(circuit, settings):
    """
    Return the body of the Latex document, including the entire circuit in
    TikZ format.

    :param Program circuit: The circuit to be drawn, represented as a pyquil program.
    :param dict settings:

    :return: Latex string to draw the entire circuit.
    :rtype: string
    """
    qubit_instruction_mapping = {}

    # Allocate each qubit.
    for inst in circuit:
        if isinstance(inst, Measurement):
            inst.qubits = [inst.qubit]
            inst.name = "MEASURE"
        elif isinstance(inst, Gate):
            for qubit in inst.qubits:
                qubit_instruction_mapping[qubit.index] = []
    for k, v in list(qubit_instruction_mapping.items()):
        v.append(command(ALLOCATE, [k], [], [k], k))

    for inst in circuit:
        # Ignore everything that is neither a Gate nor a Measurement (e.g. a Pragma)
        if not isinstance(inst, Gate) and not isinstance(inst, Measurement):
            continue
        qubits = [qubit.index for qubit in inst.qubits]
        gate = inst.name
        # If this is a single qubit instruction.
        if len(qubits) == 1:
            for qubit in qubits:
                qubit_instruction_mapping[qubit].append(command(gate, [qubit], [], [qubit], qubit))

        # If this is a many-qubit operation.
        else:
            # All qubits explicitly involved in the gate.
            explicit_lines = [qubit for qubit in copy(qubits)]
            # All lines to consider that will run through this circuit element.
            all_lines = list(range(min(explicit_lines), max(explicit_lines) + 1))
            # Include all lines that are in-use and in the range of lines used in this instruction.
            for line in all_lines:
                if line not in qubit_instruction_mapping.keys() and line in all_lines:
                    all_lines.remove(line)
            for i, qubit in enumerate(all_lines):
                if gate == CZ:
                    ctrl_lines = list(explicit_lines)
                    ctrl_lines.remove(qubits[-1])
                    qubit_instruction_mapping[qubit].append(command(Z, list(all_lines),
                                                                    list(ctrl_lines),
                                                                    qubits[-1:], None))
                elif gate == CNOT:
                    ctrl_lines = list(explicit_lines)
                    ctrl_lines.remove(qubits[-1])
                    qubit_instruction_mapping[qubit].append(command(X, list(all_lines),
                                                                    list(ctrl_lines),
                                                                    qubits[-1:], None))
                else:
                    qubit_instruction_mapping[qubit].append(command(gate, list(all_lines), [],
                                                                    list(explicit_lines), None))

    # Zero index, and remove gaps in spacing.
    relabeled_circuit = {}
    # Store a mapping so we can relabel command labels.
    index_map = {}
    for i, key in enumerate(sorted(qubit_instruction_mapping.keys())):
        relabeled_circuit[i] = qubit_instruction_mapping[key]
        index_map[key] = i

    for line in list(relabeled_circuit.values()):
        for cmd in line:
            for i, qubit in enumerate(cmd.lines):
                cmd.lines[i] = index_map[qubit]
            for i, qubit in enumerate(cmd.ctrl_lines):
                cmd.ctrl_lines[i] = index_map[qubit]
            for i, qubit in enumerate(cmd.target_lines):
                cmd.target_lines[i] = index_map[qubit]
    code_generator = CircuitTikzGenerator(settings)
    return code_generator.generate_circuit(relabeled_circuit)