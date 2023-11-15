    def _eigvals(cls, theta, pauli_word):
        return MultiRZ._eigvals(theta, len(pauli_word))