    def run(self, dag):
        """Run the SabreLayout pass on `dag`.

        Args:
            dag (DAGCircuit): DAG to find layout for.

        Raises:
            TranspilerError: if dag wider than self.coupling_map
        """
        if len(dag.qubits) > self.coupling_map.size():
            raise TranspilerError('More virtual qubits exist than physical.')

        # Choose a random initial_layout.
        if self.seed is None:
            self.seed = np.random.randint(0, np.iinfo(np.int32).max)
        rng = np.random.default_rng(self.seed)

        physical_qubits = rng.choice(self.coupling_map.size(),
                                     len(dag.qubits), replace=False)
        physical_qubits = rng.permutation(physical_qubits)
        initial_layout = Layout({q: dag.qubits[i]
                                 for i, q in enumerate(physical_qubits)})

        if self.routing_pass is None:
            self.routing_pass = SabreSwap(self.coupling_map, 'decay', seed=self.seed)

        # Do forward-backward iterations.
        circ = dag_to_circuit(dag)
        for i in range(self.max_iterations):
            for _ in ('forward', 'backward'):
                pm = self._layout_and_route_passmanager(initial_layout)
                new_circ = pm.run(circ)

                # Update initial layout and reverse the unmapped circuit.
                pass_final_layout = pm.property_set['final_layout']
                final_layout = self._compose_layouts(initial_layout,
                                                     pass_final_layout,
                                                     new_circ.qregs)
                initial_layout = final_layout
                circ = circ.reverse_ops()

            # Diagnostics
            logger.info('After round %d, num_swaps: %d',
                        i+1, new_circ.count_ops().get('swap', 0))
            logger.info('new initial layout')
            logger.info(initial_layout)

        self.property_set['layout'] = initial_layout