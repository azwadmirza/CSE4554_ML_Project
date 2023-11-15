    def get_kernel_matrix(quantum_instance, feature_map, x1_vec, x2_vec=None, enforce_psd=True):
        """
        Construct kernel matrix, if x2_vec is None, self-innerproduct is conducted.

        Notes:
            When using `statevector_simulator`,
            we only build the circuits for Psi(x1)|0> rather than
            Psi(x2)^dagger Psi(x1)|0>, and then we perform the inner product classically.
            That is, for `statevector_simulator`,
            the total number of circuits will be O(N) rather than
            O(N^2) for `qasm_simulator`.

        Args:
            quantum_instance (QuantumInstance): quantum backend with all settings
            feature_map (FeatureMap): a feature map that maps data to feature space
            x1_vec (numpy.ndarray): data points, 2-D array, N1xD, where N1 is the number of data,
                                    D is the feature dimension
            x2_vec (numpy.ndarray): data points, 2-D array, N2xD, where N2 is the number of data,
                                    D is the feature dimension
            enforce_psd (bool): enforces that the kernel matrix is positive semi-definite by setting
                                negative eigenvalues to zero. This is only applied in the symmetric
                                case, i.e., if `x2_vec == None`.
        Returns:
            numpy.ndarray: 2-D matrix, N1xN2
        """

        if isinstance(feature_map, QuantumCircuit):
            use_parameterized_circuits = True
        else:
            use_parameterized_circuits = feature_map.support_parameterized_circuit

        if x2_vec is None:
            is_symmetric = True
            x2_vec = x1_vec
        else:
            is_symmetric = False

        is_statevector_sim = quantum_instance.is_statevector

        measurement = not is_statevector_sim
        measurement_basis = '0' * feature_map.num_qubits
        mat = np.ones((x1_vec.shape[0], x2_vec.shape[0]))

        # get all indices
        if is_symmetric:
            mus, nus = np.triu_indices(x1_vec.shape[0], k=1)  # remove diagonal term
        else:
            mus, nus = np.indices((x1_vec.shape[0], x2_vec.shape[0]))
            mus = np.asarray(mus.flat)
            nus = np.asarray(nus.flat)

        if is_statevector_sim:
            if is_symmetric:
                to_be_computed_data = x1_vec
            else:
                to_be_computed_data = np.concatenate((x1_vec, x2_vec))

            if use_parameterized_circuits:
                # build parameterized circuits, it could be slower for building circuit
                # but overall it should be faster since it only transpile one circuit
                feature_map_params = ParameterVector('x', feature_map.feature_dimension)
                parameterized_circuit = QSVM._construct_circuit(
                    (feature_map_params, feature_map_params), feature_map, measurement,
                    is_statevector_sim=is_statevector_sim)
                parameterized_circuit = quantum_instance.transpile(parameterized_circuit)[0]
                circuits = [parameterized_circuit.assign_parameters({feature_map_params: x})
                            for x in to_be_computed_data]
            else:
                #  the second x is redundant
                to_be_computed_data_pair = [(x, x) for x in to_be_computed_data]
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug("Building circuits:")
                    TextProgressBar(sys.stderr)
                circuits = parallel_map(QSVM._construct_circuit,
                                        to_be_computed_data_pair,
                                        task_args=(feature_map, measurement, is_statevector_sim),
                                        num_processes=aqua_globals.num_processes)

            results = quantum_instance.execute(circuits,
                                               had_transpiled=use_parameterized_circuits)

            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("Calculating overlap:")
                TextProgressBar(sys.stderr)

            offset = 0 if is_symmetric else len(x1_vec)
            matrix_elements = parallel_map(QSVM._compute_overlap, list(zip(mus, nus + offset)),
                                           task_args=(results,
                                                      is_statevector_sim, measurement_basis),
                                           num_processes=aqua_globals.num_processes)

            for i, j, value in zip(mus, nus, matrix_elements):
                mat[i, j] = value
                if is_symmetric:
                    mat[j, i] = mat[i, j]
        else:
            for idx in range(0, len(mus), QSVM.BATCH_SIZE):
                to_be_computed_data_pair = []
                to_be_computed_index = []
                for sub_idx in range(idx, min(idx + QSVM.BATCH_SIZE, len(mus))):
                    i = mus[sub_idx]
                    j = nus[sub_idx]
                    x1 = x1_vec[i]
                    x2 = x2_vec[j]
                    if not np.all(x1 == x2):
                        to_be_computed_data_pair.append((x1, x2))
                        to_be_computed_index.append((i, j))

                if use_parameterized_circuits:
                    # build parameterized circuits, it could be slower for building circuit
                    # but overall it should be faster since it only transpile one circuit
                    feature_map_params_x = ParameterVector('x', feature_map.feature_dimension)
                    feature_map_params_y = ParameterVector('y', feature_map.feature_dimension)
                    parameterized_circuit = QSVM._construct_circuit(
                        (feature_map_params_x, feature_map_params_y), feature_map, measurement,
                        is_statevector_sim=is_statevector_sim)
                    parameterized_circuit = quantum_instance.transpile(parameterized_circuit)[0]
                    circuits = [parameterized_circuit.assign_parameters({feature_map_params_x: x,
                                                                         feature_map_params_y: y})
                                for x, y in to_be_computed_data_pair]
                else:
                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug("Building circuits:")
                        TextProgressBar(sys.stderr)
                    circuits = parallel_map(QSVM._construct_circuit,
                                            to_be_computed_data_pair,
                                            task_args=(feature_map, measurement),
                                            num_processes=aqua_globals.num_processes)

                results = quantum_instance.execute(circuits,
                                                   had_transpiled=use_parameterized_circuits)

                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug("Calculating overlap:")
                    TextProgressBar(sys.stderr)
                matrix_elements = parallel_map(QSVM._compute_overlap, range(len(circuits)),
                                               task_args=(results,
                                                          is_statevector_sim, measurement_basis),
                                               num_processes=aqua_globals.num_processes)

                for (i, j), value in zip(to_be_computed_index, matrix_elements):
                    mat[i, j] = value
                    if is_symmetric:
                        mat[j, i] = mat[i, j]

        if enforce_psd and is_symmetric and not is_statevector_sim:
            # Find the closest positive semi-definite approximation to kernel matrix, in case it is
            # symmetric. The (symmetric) matrix should always be positive semi-definite by
            # construction, but this can be violated in case of noise, such as sampling noise, thus,
            # the adjustment is only done if NOT using the statevector simulation.
            D, U = np.linalg.eig(mat)
            mat = U @ np.diag(np.maximum(0, D)) @ U.transpose()

        return mat