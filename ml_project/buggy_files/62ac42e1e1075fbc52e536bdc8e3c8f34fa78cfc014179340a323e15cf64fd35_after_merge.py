def _transpilation(circuit, basis_gates=None, coupling_map=None,
                   initial_layout=None, seed_mapper=None,
                   pass_manager=None):
    """Perform transpilation of a single circuit.

    Args:
        circuit (QuantumCircuit): A circuit to transpile.
        basis_gates (list[str]): list of basis gate names supported by the
            target. Default: ['u1','u2','u3','cx','id']
        coupling_map (CouplingMap): coupling map (perhaps custom) to target in mapping
        initial_layout (Layout): initial layout of qubits in mapping
        seed_mapper (int): random seed for the swap_mapper
        pass_manager (PassManager): a pass_manager for the transpiler stage

    Returns:
        QuantumCircuit: A transpiled circuit.

    Raises:
        TranspilerError: If the Layout does not matches the circuit
    """
    if initial_layout is not None and set(circuit.qregs) != initial_layout.get_registers():
        raise TranspilerError('The provided initial layout does not match the registers in '
                              'the circuit "%s"' % circuit.name)

    if pass_manager and not pass_manager.working_list:
        return circuit

    is_parametric_circuit = bool(circuit.unassigned_variables)

    dag = circuit_to_dag(circuit)
    del circuit

    final_dag = transpile_dag(dag, basis_gates=basis_gates,
                              coupling_map=coupling_map,
                              initial_layout=initial_layout,
                              skip_numeric_passes=is_parametric_circuit,
                              seed_mapper=seed_mapper,
                              pass_manager=pass_manager)

    out_circuit = dag_to_circuit(final_dag)

    return out_circuit