    def _eigvals(cls, theta, pauli_word):
        # Identity must be treated specially because its eigenvalues are all the same
        if pauli_word == "I" * len(pauli_word):
            return np.exp(-1j * theta / 2) * np.ones(2 ** len(pauli_word))

        return MultiRZ._eigvals(theta, len(pauli_word))