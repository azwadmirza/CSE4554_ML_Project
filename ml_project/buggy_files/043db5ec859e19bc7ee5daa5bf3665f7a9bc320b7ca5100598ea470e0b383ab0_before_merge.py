    def __new__(cls, num_ctrl_qubits=None, label=None, ctrl_state=None):
        """Create a new MCX instance.

        Depending on the number of controls, this creates an explicit X, CX, CCX, C3X or C4X
        instance or a generic MCX gate.
        """
        # these gates will always be implemented for all modes of the MCX if the number of control
        # qubits matches this
        explicit = {
            1: CXGate,
            2: CCXGate
        }
        if num_ctrl_qubits == 0:
            return XGate(label=label)
        if num_ctrl_qubits in explicit.keys():
            gate_class = explicit[num_ctrl_qubits]
            gate = gate_class.__new__(gate_class, label=label, ctrl_state=ctrl_state)
            # if __new__ does not return the same type as cls, init is not called
            gate.__init__(label=label, ctrl_state=ctrl_state)
            return gate
        return super().__new__(cls)