    def apply_operation_back(self, op, qargs=None, cargs=None, condition=None):
        """Apply an operation to the output of the circuit.

        Args:
            op (Instruction): the operation associated with the DAG node
            qargs (list[Qubit]): qubits that op will be applied to
            cargs (list[Clbit]): cbits that op will be applied to
            condition (tuple or None): optional condition (ClassicalRegister, int)

        Returns:
            DAGNode: the current max node

        Raises:
            DAGCircuitError: if a leaf node is connected to multiple outputs

        """
        qargs = qargs or []
        cargs = cargs or []

        all_cbits = self._bits_in_condition(condition)
        all_cbits.extend(cargs)

        self._check_condition(op.name, condition)
        self._check_bits(qargs, self.output_map)
        self._check_bits(all_cbits, self.output_map)

        self._add_op_node(op, qargs, cargs, condition)

        # Add new in-edges from predecessors of the output nodes to the
        # operation node while deleting the old in-edges of the output nodes
        # and adding new edges from the operation node to each output node
        al = [qargs, all_cbits]
        for q in itertools.chain(*al):
            ie = list(self._multi_graph.predecessors(self.output_map[q]))

            if len(ie) != 1:
                raise DAGCircuitError("output node has multiple in-edges")

            self._multi_graph.add_edge(ie[0], self._id_to_node[self._max_node_id],
                                       name="%s[%s]" % (q.register.name, q.index), wire=q)
            self._multi_graph.remove_edge(ie[0], self.output_map[q])
            self._multi_graph.add_edge(self._id_to_node[self._max_node_id], self.output_map[q],
                                       name="%s[%s]" % (q.register.name, q.index), wire=q)

        return self._id_to_node[self._max_node_id]