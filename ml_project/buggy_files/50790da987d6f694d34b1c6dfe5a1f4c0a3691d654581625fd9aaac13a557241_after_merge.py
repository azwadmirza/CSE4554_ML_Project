    def expand_gates(self, basis=None):
        """Expand all gate nodes to the given basis.

        If basis is empty, each custom gate node is replaced by its
        implementation over U and CX. If basis contains names, then
        those custom gates are not expanded. For example, if "u3"
        is in basis, then the gate "u3" will not be expanded wherever
        it occurs.

        This member function replicates the behavior of the unroller
        module without using the OpenQASM parser.
        """

        if basis is None:
            basis = self.backend.basis

        if not isinstance(self.backend, DAGBackend):
            raise UnrollerError("expand_gates only accepts a DAGBackend!!")

        # Build the Gate AST nodes for user-defined gates
        gatedefs = []
        for name, gate in self.dag_circuit.gates.items():
            children = [Id(name, 0, "")]
            if gate["n_args"] > 0:
                children.append(ExpressionList(list(
                    map(lambda x: Id(x, 0, ""),
                        gate["args"])
                )))
            children.append(IdList(list(
                map(lambda x: Id(x, 0, ""),
                    gate["bits"])
            )))
            children.append(gate["body"])
            gatedefs.append(Gate(children))
        # Walk through the DAG and examine each node
        builtins = ["U", "CX", "measure", "reset", "barrier"]
        simulator_builtins = ['snapshot', 'save', 'load', 'noise']
        topological_sorted_list = list(nx.topological_sort(self.dag_circuit.multi_graph))
        for node in topological_sorted_list:
            current_node = self.dag_circuit.multi_graph.node[node]
            if current_node["type"] == "op" and \
               current_node["name"] not in builtins + basis + simulator_builtins and \
               not self.dag_circuit.gates[current_node["name"]]["opaque"]:
                subcircuit, wires = self._build_subcircuit(gatedefs,
                                                           basis,
                                                           current_node["name"],
                                                           current_node["params"],
                                                           current_node["qargs"],
                                                           current_node["condition"])
                self.dag_circuit.substitute_circuit_one(node, subcircuit, wires)
        return self.dag_circuit