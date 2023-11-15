def run_bell_low_level(n_shots=1000):
    # Step 1. Get some device components
    qc = get_qc('9q-generic-qvm')
    compiler = qc.compiler
    qam = qc.qam
    del qc

    q = [4, 5]  # qubits

    # Step 2. Construct your program
    program = Program()
    program += H(q[0])
    program += CNOT(q[0], q[1])

    # Step 2.1. Manage read-out memory
    ro = program.declare('ro', memory_type='BIT', memory_size='2')
    program += MEASURE(q[0], ro[0])
    program += MEASURE(q[1], ro[1])

    # Step 2.2. Run the program in a loop
    program = program.wrap_in_numshots_loop(n_shots)

    # Step 3. Compile and run
    nq_program = compiler.quil_to_native_quil(program)
    executable = compiler.native_quil_to_executable(nq_program)
    bitstrings = qam.load(executable) \
        .run() \
        .wait() \
        .read_from_memory_region(region_name="ro", offsets=True)

    # Bincount bitstrings
    basis = np.array([2 ** i for i in range(len(q))])
    ints = np.sum(bitstrings * basis, axis=1)
    print('bincounts', np.bincount(ints))

    # Check parity
    parities = np.sum(bitstrings, axis=1) % 2
    print('avg parity', np.mean(parities))