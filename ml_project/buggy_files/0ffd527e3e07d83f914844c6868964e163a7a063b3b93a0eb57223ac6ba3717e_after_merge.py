    def substitute_node_with_dag(self, node, input_dag, wires=None):
        """Replace one node with dag.

        Args:
            node (DAGNode): node to substitute
            input_dag (DAGCircuit): circuit that will substitute the node
            wires (list[(Register, index)]): gives an order for (qu)bits
                in the input circuit. This order gets matched to the node wires
                by qargs first, then cargs, then conditions.

        Raises:
            DAGCircuitError: if met with unexpected predecessor/successors
        """
        condition = node.condition
        # the dag must be amended if used in a
        # conditional context. delete the op nodes and replay
        # them with the condition.
        if condition:
            input_dag.add_creg(condition[0])
            to_replay = []
            for sorted_node in input_dag.topological_nodes():
                if sorted_node.type == "op":
                    sorted_node.op.control = condition
                    to_replay.append(sorted_node)
            for input_node in input_dag.op_nodes():
                input_dag.remove_op_node(input_node)
            for replay_node in to_replay:
                input_dag.apply_operation_back(replay_node.op, replay_node.qargs,
                                               replay_node.cargs, condition=condition)

        if wires is None:
            qwires = [w for w in input_dag.wires if isinstance(w, Qubit)]
            cwires = [w for w in input_dag.wires if isinstance(w, Clbit)]
            wires = qwires + cwires

        self._check_wires_list(wires, node)

        # Create a proxy wire_map to identify fragments and duplicates
        # and determine what registers need to be added to self
        proxy_map = {w: QuantumRegister(1, 'proxy') for w in wires}
        add_qregs = self._check_edgemap_registers(proxy_map,
                                                  input_dag.qregs,
                                                  {}, False)
        for qreg in add_qregs:
            self.add_qreg(qreg)

        add_cregs = self._check_edgemap_registers(proxy_map,
                                                  input_dag.cregs,
                                                  {}, False)
        for creg in add_cregs:
            self.add_creg(creg)

        # Replace the node by iterating through the input_circuit.
        # Constructing and checking the validity of the wire_map.
        # If a gate is conditioned, we expect the replacement subcircuit
        # to depend on those control bits as well.
        if node.type != "op":
            raise DAGCircuitError("expected node type \"op\", got %s"
                                  % node.type)

        condition_bit_list = self._bits_in_condition(node.condition)

        wire_map = {k: v for k, v in zip(wires,
                                         [i for s in [node.qargs,
                                                      node.cargs,
                                                      condition_bit_list]
                                          for i in s])}
        self._check_wiremap_validity(wire_map, wires, self.input_map)
        pred_map, succ_map = self._make_pred_succ_maps(node)
        full_pred_map, full_succ_map = self._full_pred_succ_maps(pred_map, succ_map,
                                                                 input_dag, wire_map)

        if condition_bit_list:
            # If we are replacing a conditional node, map input dag through
            # wire_map to verify that it will not modify any of the conditioning
            # bits.
            condition_bits = set(condition_bit_list)

            for op_node in input_dag.op_nodes():
                mapped_cargs = {wire_map[carg] for carg in op_node.cargs}

                if condition_bits & mapped_cargs:
                    raise DAGCircuitError('Mapped DAG would alter clbits '
                                          'on which it would be conditioned.')

        # Now that we know the connections, delete node
        self._multi_graph.remove_node(node)

        # Iterate over nodes of input_circuit
        for sorted_node in input_dag.topological_op_nodes():
            # Insert a new node
            condition = self._map_condition(wire_map, sorted_node.condition)
            m_qargs = list(map(lambda x: wire_map.get(x, x),
                               sorted_node.qargs))
            m_cargs = list(map(lambda x: wire_map.get(x, x),
                               sorted_node.cargs))
            self._add_op_node(sorted_node.op, m_qargs, m_cargs, condition)
            # Add edges from predecessor nodes to new node
            # and update predecessor nodes that change
            all_cbits = self._bits_in_condition(condition)
            all_cbits.extend(m_cargs)
            al = [m_qargs, all_cbits]
            for q in itertools.chain(*al):
                self._multi_graph.add_edge(full_pred_map[q],
                                           self._id_to_node[self._max_node_id],
                                           name="%s[%s]" % (q.register.name, q.index),
                                           wire=q)
                full_pred_map[q] = self._id_to_node[self._max_node_id]

        # Connect all predecessors and successors, and remove
        # residual edges between input and output nodes
        for w in full_pred_map:
            self._multi_graph.add_edge(full_pred_map[w],
                                       full_succ_map[w],
                                       name="%s[%s]" % (w.register.name, w.index),
                                       wire=w)
            o_pred = list(self._multi_graph.predecessors(self.output_map[w]))
            if len(o_pred) > 1:
                if len(o_pred) != 2:
                    raise DAGCircuitError("expected 2 predecessors here")

                p = [x for x in o_pred if x != full_pred_map[w]]
                if len(p) != 1:
                    raise DAGCircuitError("expected 1 predecessor to pass filter")

                self._multi_graph.remove_edge(p[0], self.output_map[w])