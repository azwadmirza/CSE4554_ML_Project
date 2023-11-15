    def dagger(self, inv_dict=None, suffix="-INV"):
        """
        Creates the conjugate transpose of the Quil program. The program must not
        contain any irreversible actions (measurement, control flow, qubit allocation).

        :return: The Quil program's inverse
        :rtype: Program

        """
        if not self.is_protoquil():
            raise ValueError("Program must be valid Protoquil")

        daggered = Program()

        for gate in self._defined_gates:
            if inv_dict is None or gate.name not in inv_dict:
                if gate.parameters:
                    raise TypeError("Cannot auto define daggered version of parameterized gates")
                daggered.defgate(gate.name + suffix, gate.matrix.T.conj())

        for gate in reversed(self._instructions):
            if gate.name in STANDARD_GATES:
                if gate.name == "S":
                    daggered.inst(STANDARD_GATES["PHASE"](-pi / 2, *gate.qubits))
                elif gate.name == "T":
                    daggered.inst(STANDARD_GATES["RZ"](pi / 4, *gate.qubits))
                elif gate.name == "ISWAP":
                    daggered.inst(STANDARD_GATES["PSWAP"](pi / 2, *gate.qubits))
                else:
                    negated_params = list(map(lambda x: -1 * x, gate.params))
                    daggered.inst(STANDARD_GATES[gate.name](*(negated_params + gate.qubits)))
            else:
                if inv_dict is None or gate.name not in inv_dict:
                    gate_inv_name = gate.name + suffix
                else:
                    gate_inv_name = inv_dict[gate.name]

                daggered.inst(Gate(gate_inv_name, gate.params, gate.qubits))

        return daggered