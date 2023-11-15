    def _select_best_remaining_cx(self):
        """
        Select best remaining CNOT in the hardware for the next program edge.
        """
        candidates = []
        for gate in self.gate_list:
            chk1 = gate[0] in self.available_hw_qubits
            chk2 = gate[1] in self.available_hw_qubits
            if chk1 and chk2:
                candidates.append(gate)
        best_reliab = 0
        best_item = None
        for item in candidates:
            if self.gate_cost[item] > best_reliab:
                best_reliab = self.gate_cost[item]
                best_item = item
        return best_item