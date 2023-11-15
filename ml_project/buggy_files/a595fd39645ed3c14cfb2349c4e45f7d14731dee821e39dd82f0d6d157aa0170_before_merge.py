def run_bell_high_level(n_shots=1000):
    # Step 1. Get a device. Either a QVM or a QPU
    qc = get_qc('9q-generic-qvm')
    q = [4, 5]  # qubits

    # Step 2. Construct your program
    program = Program(
        H(q[0]),
        CNOT(q[0], q[1])
    )

    # Step 3. Run
    bitstrings = qc.run_and_measure(program, trials=n_shots)

    # Bincount bitstrings
    basis = np.array([2 ** i for i in range(len(q))])
    ints = np.sum(bitstrings * basis, axis=1)
    print('bincounts', np.bincount(ints))

    # Check parity
    parities = np.sum(bitstrings, axis=1) % 2
    print('avg parity', np.mean(parities))