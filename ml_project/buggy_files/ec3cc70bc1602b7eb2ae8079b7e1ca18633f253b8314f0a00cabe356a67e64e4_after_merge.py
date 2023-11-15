def unitary(self, obj, qubits, label=None):
    """Apply unitary gate to q."""
    gate = UnitaryGate(obj, label=label)
    if isinstance(qubits, QuantumRegister):
        qubits = qubits[:]
    # for single qubit unitary gate, allow an 'int' or a 'list of ints' as qubits.
    if gate.num_qubits == 1:
        if isinstance(qubits, (int, Qubit)) or len(qubits) > 1:
            qubits = [qubits]
    return self.append(gate, qubits, [])