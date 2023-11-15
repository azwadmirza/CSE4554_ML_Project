def unitary(self, obj, qubits, label=None):
    """Apply unitary gate to q."""
    if isinstance(qubits, QuantumRegister):
        qubits = qubits[:]
    return self.append(UnitaryGate(obj, label=label), qubits, [])