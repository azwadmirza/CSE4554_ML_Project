    def __init__(self, name: str, num_qubits: int, params: List,
                 label: Optional[str] = None, num_ctrl_qubits: Optional[int] = 1,
                 definition: Optional[List[Tuple[Gate, List[Qubit], List[Clbit]]]] = None,
                 ctrl_state: Optional[Union[int, str]] = None):
        """Create a new ControlledGate. In the new gate the first ``num_ctrl_qubits``
        of the gate are the controls.

        Args:
            name: The name of the gate.
            num_qubits: The number of qubits the gate acts on.
            params: A list of parameters for the gate.
            label: An optional label for the gate.
            num_ctrl_qubits: Number of control qubits.
            definition: A list of gate rules for implementing this gate. The
                elements of the list are tuples of (:meth:`~qiskit.circuit.Gate`, [qubit_list],
                [clbit_list]).
            ctrl_state: The control state in decimal or as
                a bitstring (e.g. '111'). If specified as a bitstring the length
                must equal num_ctrl_qubits, MSB on left. If None, use
                2**num_ctrl_qubits-1.

        Raises:
            CircuitError: If ``num_ctrl_qubits`` >= ``num_qubits``.
            CircuitError: ctrl_state < 0 or ctrl_state > 2**num_ctrl_qubits.

        Examples:

        Create a controlled standard gate and apply it to a circuit.

        .. jupyter-execute::

           from qiskit import QuantumCircuit, QuantumRegister
           from qiskit.circuit.library.standard_gates import HGate

           qr = QuantumRegister(3)
           qc = QuantumCircuit(qr)
           c3h_gate = HGate().control(2)
           qc.append(c3h_gate, qr)
           qc.draw()

        Create a controlled custom gate and apply it to a circuit.

        .. jupyter-execute::

           from qiskit import QuantumCircuit, QuantumRegister
           from qiskit.circuit.library.standard_gates import HGate

           qc1 = QuantumCircuit(2)
           qc1.x(0)
           qc1.h(1)
           custom = qc1.to_gate().control(2)

           qc2 = QuantumCircuit(4)
           qc2.append(custom, [0, 3, 1, 2])
           qc2.draw()
        """
        super().__init__(name, num_qubits, params, label=label)
        if num_ctrl_qubits < num_qubits:
            self.num_ctrl_qubits = num_ctrl_qubits
        else:
            raise CircuitError('number of control qubits must be less than the number of qubits')
        self.base_gate = None
        if definition:
            self.definition = definition
            if len(definition) == 1:
                base_gate = definition[0][0]
                if isinstance(base_gate, ControlledGate):
                    self.base_gate = base_gate.base_gate
                else:
                    self.base_gate = base_gate
        self._ctrl_state = None
        self.ctrl_state = ctrl_state