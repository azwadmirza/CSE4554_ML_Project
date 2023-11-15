    def _get_probs(self, qc: QuantumCircuit) -> Dict[str, float]:
        """Gets probabilities from a given backend."""
        # Execute job and filter results.
        result = self.quantum_instance.execute(qc)
        if self.quantum_instance.is_statevector:
            state = np.round(result.get_statevector(qc), 5)
            keys = [bin(i)[2::].rjust(int(np.log2(len(state))), '0')[::-1]
                    for i in range(0, len(state))]
            probs = [np.round(abs(a) * abs(a), 5) for a in state]
            hist = dict(zip(keys, probs))
        else:
            state = result.get_counts(qc)
            shots = self.quantum_instance.run_config.shots
            hist = {}
            for key in state:
                hist[key] = state[key] / shots
        hist = dict(filter(lambda p: p[1] > 0, hist.items()))

        return hist