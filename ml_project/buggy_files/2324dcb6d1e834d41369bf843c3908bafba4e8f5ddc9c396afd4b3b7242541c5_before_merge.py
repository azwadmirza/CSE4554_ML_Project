def control(operation: Union[Gate, ControlledGate],
            num_ctrl_qubits: Optional[int] = 1,
            label: Optional[Union[None, str]] = None,
            ctrl_state: Optional[Union[None, int, str]] = None) -> ControlledGate:
    """Return controlled version of gate using controlled rotations. This function
    first checks the name of the operation to see if it knows of a method from which
    to generate a controlled version. Currently these are `x`, `rx`, `ry`, and `rz`.
    If a method is not directly known, it calls the unroller to convert to `u1`, `u3`,
    and `cx` gates.

    Args:
        operation: The gate used to create the ControlledGate.
        num_ctrl_qubits: The number of controls to add to gate (default=1).
        label: An optional gate label.
        ctrl_state: The control state in decimal or as
            a bitstring (e.g. '111'). If specified as a bitstring the length
            must equal num_ctrl_qubits, MSB on left. If None, use
            2**num_ctrl_qubits-1.

    Returns:
        Controlled version of gate.

    Raises:
        CircuitError: gate contains non-gate in definition
    """
    from math import pi
    # pylint: disable=cyclic-import
    import qiskit.circuit.controlledgate as controlledgate
    # pylint: disable=unused-import
    import qiskit.circuit.library.standard_gates.multi_control_rotation_gates

    # check args
    if num_ctrl_qubits == 0:
        return operation
    elif num_ctrl_qubits < 0:
        raise CircuitError('number of control qubits must be positive integer')

    q_control = QuantumRegister(num_ctrl_qubits, name='control')
    q_target = QuantumRegister(operation.num_qubits, name='target')
    q_ancillae = None  # TODO: add
    qc = QuantumCircuit(q_control, q_target)

    if operation.name == 'x' or (
            isinstance(operation, controlledgate.ControlledGate) and
            operation.base_gate.name == 'x'):
        qc.mct(q_control[:] + q_target[:-1], q_target[-1], q_ancillae)
    elif operation.name == 'rx':
        qc.mcrx(operation.definition[0][0].params[0], q_control, q_target[0],
                use_basis_gates=True)
    elif operation.name == 'ry':
        qc.mcry(operation.definition[0][0].params[0], q_control, q_target[0],
                q_ancillae, mode='noancilla', use_basis_gates=True)
    elif operation.name == 'rz':
        qc.mcrz(operation.definition[0][0].params[0], q_control, q_target[0],
                use_basis_gates=True)
    else:
        bgate = _unroll_gate(operation, ['u1', 'u3', 'cx'])
        # now we have a bunch of single qubit rotation gates and cx
        for rule in bgate.definition:
            if rule[0].name == 'u3':
                theta, phi, lamb = rule[0].params
                if phi == -pi / 2 and lamb == pi / 2:
                    qc.mcrx(theta, q_control, q_target[rule[1][0].index],
                            use_basis_gates=True)
                elif phi == 0 and lamb == 0:
                    qc.mcry(theta, q_control, q_target[rule[1][0].index],
                            q_ancillae, use_basis_gates=True)
                elif theta == 0 and phi == 0:
                    qc.mcrz(lamb, q_control, q_target[rule[1][0].index],
                            use_basis_gates=True)
                else:
                    qc.mcrz(lamb, q_control, q_target[rule[1][0].index],
                            use_basis_gates=True)
                    qc.mcry(theta, q_control, q_target[rule[1][0].index],
                            q_ancillae, use_basis_gates=True)
                    qc.mcrz(phi, q_control, q_target[rule[1][0].index],
                            use_basis_gates=True)
            elif rule[0].name == 'u1':
                qc.mcu1(rule[0].params[0], q_control, q_target[rule[1][0].index])
            elif rule[0].name == 'cx':
                qc.mct(q_control[:] + [q_target[rule[1][0].index]], q_target[rule[1][1].index],
                       q_ancillae)
            else:
                raise CircuitError('gate contains non-controllable instructions')

    instr = qc.to_instruction()
    if isinstance(operation, controlledgate.ControlledGate):
        new_num_ctrl_qubits = num_ctrl_qubits + operation.num_ctrl_qubits
        new_ctrl_state = operation.ctrl_state << num_ctrl_qubits | ctrl_state
        base_name = operation.base_gate.name
        base_gate = operation.base_gate
    else:
        new_num_ctrl_qubits = num_ctrl_qubits
        new_ctrl_state = ctrl_state
        base_name = operation.name
        base_gate = operation
    # In order to maintain some backward compatibility with gate names this
    # uses a naming convention where if the number of controls is <=2 the gate
    # is named like "cc<base_gate.name>", else it is named like
    # "c<num_ctrl_qubits><base_name>".
    if new_num_ctrl_qubits > 2:
        ctrl_substr = 'c{0:d}'.format(new_num_ctrl_qubits)
    else:
        ctrl_substr = ('{0}' * new_num_ctrl_qubits).format('c')
    new_name = '{0}{1}'.format(ctrl_substr, base_name)
    cgate = controlledgate.ControlledGate(new_name,
                                          instr.num_qubits,
                                          operation.params,
                                          label=label,
                                          num_ctrl_qubits=new_num_ctrl_qubits,
                                          definition=instr.definition,
                                          ctrl_state=new_ctrl_state)
    cgate.base_gate = base_gate
    return cgate