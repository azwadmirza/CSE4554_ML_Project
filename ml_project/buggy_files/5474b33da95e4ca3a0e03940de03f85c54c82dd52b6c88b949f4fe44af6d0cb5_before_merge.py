    def __init__(self, *params, wires=None, do_queue=True):
        super().__init__(*params, wires=wires, do_queue=True)

        pauli_word = params[1]

        if not PauliRot._check_pauli_word(pauli_word):
            raise ValueError(
                'The given Pauli word "{}" contains characters that are not allowed.'
                " Allowed characters are I, X, Y and Z".format(pauli_word)
            )

        if not len(pauli_word) == len(wires):
            raise ValueError(
                "The given Pauli word has length {}, length {} was expected for wires {}".format(
                    len(pauli_word), len(wires), wires
                )
            )