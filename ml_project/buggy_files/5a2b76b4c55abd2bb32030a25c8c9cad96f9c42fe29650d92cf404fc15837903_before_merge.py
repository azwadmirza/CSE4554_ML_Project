    def decomposition(theta, pauli_word, wires):
        active_wires, active_gates = zip(
            *[(wire, gate) for wire, gate in zip(wires, pauli_word) if gate != "I"]
        )

        for wire, gate in zip(active_wires, active_gates):
            if gate == "X":
                Hadamard(wires=[wire])
            elif gate == "Y":
                RX(np.pi / 2, wires=[wire])

        MultiRZ(theta, wires=list(active_wires))

        for wire, gate in zip(active_wires, active_gates):
            if gate == "X":
                Hadamard(wires=[wire])
            elif gate == "Y":
                RX(-np.pi / 2, wires=[wire])