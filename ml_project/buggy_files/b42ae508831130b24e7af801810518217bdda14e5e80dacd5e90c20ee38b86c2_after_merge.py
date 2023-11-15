    def _select_best_remaining_qubit(self, prog_qubit):
        """
        Select the best remaining hardware qubit for the next program qubit.
        """
        reliab_store = {}
        for hw_qubit in self.available_hw_qubits:
            reliab = 1
            for n in self.prog_graph.neighbors(prog_qubit):
                if n in self.prog2hw:
                    reliab *= self.swap_costs[self.prog2hw[n]][hw_qubit]
            reliab *= self.readout_reliability[hw_qubit]
            reliab_store[hw_qubit] = reliab
        max_reliab = 0
        best_hw_qubit = None
        for hw_qubit in reliab_store:
            if reliab_store[hw_qubit] > max_reliab:
                max_reliab = reliab_store[hw_qubit]
                best_hw_qubit = hw_qubit
        return best_hw_qubit