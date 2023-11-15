    def _matrix(cls, *params):
        theta = params[0]
        pauli_word = params[1]

        if not PauliRot._check_pauli_word(pauli_word):
            raise ValueError(
                'The given Pauli word "{}" contains characters that are not allowed.'
                " Allowed characters are I, X, Y and Z".format(pauli_word)
            )

        # Simplest case is if the Pauli is the identity matrix
        if pauli_word == "I" * len(pauli_word):
            return np.exp(-1j * theta / 2) * np.eye(2 ** len(pauli_word))

        # We first generate the matrix excluding the identity parts and expand it afterwards.
        # To this end, we have to store on which wires the non-identity parts act
        non_identity_wires, non_identity_gates = zip(
            *[(wire, gate) for wire, gate in enumerate(pauli_word) if gate != "I"]
        )

        multi_Z_rot_matrix = MultiRZ._matrix(theta, len(non_identity_gates))

        # now we conjugate with Hadamard and RX to create the Pauli string
        conjugation_matrix = functools.reduce(
            np.kron,
            [PauliRot._PAULI_CONJUGATION_MATRICES[gate] for gate in non_identity_gates],
        )

        return expand(
            conjugation_matrix.T.conj() @ multi_Z_rot_matrix @ conjugation_matrix,
            non_identity_wires,
            list(range(len(pauli_word))),
        )