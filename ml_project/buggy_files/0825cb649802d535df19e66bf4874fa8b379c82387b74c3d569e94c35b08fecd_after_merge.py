def compile(circuits, backend,
            config=None, basis_gates=None, coupling_map=None, initial_layout=None,
            shots=1024, max_credits=10, seed=None, qobj_id=None, hpc=None,
            skip_translation=False):
    """Compile a list of circuits into a qobj.

    FIXME THIS FUNCTION WILL BE REWRITTEN IN VERSION 0.6. It will be a thin wrapper
    of circuit->dag, transpiler (dag -> dag) and dags-> qobj

    Args:
        circuits (QuantumCircuit or list[QuantumCircuit]): circuits to compile
        backend (BaseBackend): a backend to compile for
        config (dict): dictionary of parameters (e.g. noise) used by runner
        basis_gates (str): comma-separated basis gate set to compile to
        coupling_map (list): coupling map (perhaps custom) to target in mapping
        initial_layout (list): initial layout of qubits in mapping
        shots (int): number of repetitions of each circuit, for sampling
        max_credits (int): maximum credits to use
        seed (int): random seed for simulators
        qobj_id (int): identifier for the generated qobj
        hpc (dict): HPC simulator parameters
        skip_translation (bool): If True, bypass most of the compilation process and
            creates a qobj with minimal check nor translation

    Returns:
        obj: the qobj to be run on the backends

    Raises:
        QISKitError: if any of the circuit names cannot be found on the
            Quantum Program.
    """
    if isinstance(circuits, QuantumCircuit):
        circuits = [circuits]

    backend_conf = backend.configuration
    backend_name = backend_conf['name']

    qobj = {}
    if not qobj_id:
        qobj_id = "".join([random.choice(string.ascii_letters + string.digits)
                           for n in range(30)])
    qobj['id'] = qobj_id
    qobj['config'] = {'max_credits': max_credits,
                      'shots': shots,
                      'backend_name': backend_name}

    if hpc is not None and \
            not all(key in hpc for key in ('multi_shot_optimization', 'omp_num_threads')):
        raise QISKitError('Unknown HPC parameter format!')

    qobj['circuits'] = []
    if not basis_gates:
        if 'basis_gates' in backend_conf:
            basis_gates = backend_conf['basis_gates']
    if len(basis_gates.split(',')) < 2:
        # catches deprecated basis specification like 'SU2+CNOT'
        logger.warning('encountered deprecated basis specification: '
                       '"%s" substituting u1,u2,u3,cx,id', str(basis_gates))
        basis_gates = 'u1,u2,u3,cx,id'
    if not coupling_map:
        coupling_map = backend_conf['coupling_map']

    for circuit in circuits:
        num_qubits = sum((len(qreg) for qreg in circuit.get_qregs().values()))
        # TODO: A better solution is to have options to enable/disable optimizations
        if num_qubits == 1:
            coupling_map = None
        if coupling_map == 'all-to-all':
            coupling_map = None

        # making the job to be added to qobj
        job = {}
        job["name"] = circuit.name
        # config parameters used by the runner
        if config is None:
            config = {}  # default to empty config dict
        job["config"] = copy.deepcopy(config)
        job["config"]["coupling_map"] = coupling_map
        # TODO: Jay: make config options optional for different backends
        job["config"]["basis_gates"] = basis_gates
        if seed is None:
            job["config"]["seed"] = None
        else:
            job["config"]["seed"] = seed

        if skip_translation:  # Just return the qobj, without any transformation or analysis
            job["config"]["layout"] = None
            job["compiled_circuit_qasm"] = circuit.qasm()
            job["compiled_circuit"] = DagUnroller(
                DAGCircuit.fromQuantumCircuit(circuit),
                JsonBackend(job['config']['basis_gates'].split(','))).execute()
        else:
            # Pick good initial layout if None is given and not simulator
            if initial_layout is None and not backend.configuration['simulator']:
                best_sub = best_subset(backend, num_qubits)
                initial_layout = {}
                map_iter = 0
                for key, value in circuit.get_qregs().items():
                    for i in range(value.size):
                        initial_layout[(key, i)] = ('q', best_sub[map_iter])
                        map_iter += 1

            dag_circuit, final_layout = compile_circuit(
                circuit,
                basis_gates=basis_gates,
                coupling_map=coupling_map,
                initial_layout=initial_layout,
                get_layout=True)
            # Map the layout to a format that can be json encoded
            list_layout = None
            if final_layout:
                list_layout = [[k, v] for k, v in final_layout.items()]
            job["config"]["layout"] = list_layout

            # the compiled circuit to be run saved as a dag
            # we assume that compile_circuit has already expanded gates
            # to the target basis, so we just need to generate json
            json_circuit = DagUnroller(dag_circuit, JsonBackend(dag_circuit.basis)).execute()
            job["compiled_circuit"] = json_circuit
            # set eval_symbols=True to evaluate each symbolic expression
            # TODO after transition to qobj, we can drop this
            job["compiled_circuit_qasm"] = dag_circuit.qasm(qeflag=True,
                                                            eval_symbols=True)
        # add job to the qobj
        qobj["circuits"].append(job)
    return qobj