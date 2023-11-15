    def run(self, dag):
        """iterate over each block and replace it with an equivalent Unitary
        on the same wires.
        """
        new_dag = DAGCircuit()
        for qreg in dag.qregs.values():
            new_dag.add_qreg(qreg)
        for creg in dag.cregs.values():
            new_dag.add_creg(creg)

        # compute ordered indices for the global circuit wires
        global_index_map = {}
        for wire in dag.wires:
            if not isinstance(wire, Qubit):
                continue
            global_qregs = list(dag.qregs.values())
            global_index_map[wire] = global_qregs.index(wire.register) + wire.index

        blocks = self.property_set['block_list']
        # just to make checking if a node is in any block easier
        all_block_nodes = {nd for bl in blocks for nd in bl}

        for node in dag.topological_op_nodes():
            if node not in all_block_nodes:
                # need to add this node to find out where in the list it goes
                preds = [nd for nd in dag.predecessors(node) if nd.type == 'op']

                block_count = 0
                while preds:
                    if block_count < len(blocks):
                        block = blocks[block_count]

                        # if any of the predecessors are in the block, remove them
                        preds = [p for p in preds if p not in block]
                    else:
                        # should never occur as this would mean not all
                        # nodes before this one topologically had been added
                        # so not all predecessors were removed
                        raise TranspilerError("Not all predecessors removed due to error"
                                              " in topological order")

                    block_count += 1

                # we have now seen all predecessors
                # so update the blocks list to include this block
                blocks = blocks[:block_count] + [[node]] + blocks[block_count:]

        # create the dag from the updated list of blocks
        basis_gate_name = self.decomposer.gate.name
        for block in blocks:

            if len(block) == 1 and block[0].name != 'cx':
                # an intermediate node that was added into the overall list
                new_dag.apply_operation_back(block[0].op, block[0].qargs,
                                             block[0].cargs, block[0].condition)
            else:
                # find the qubits involved in this block
                block_qargs = set()
                for nd in block:
                    block_qargs |= set(nd.qargs)
                # convert block to a sub-circuit, then simulate unitary and add
                block_width = len(block_qargs)
                q = QuantumRegister(block_width)
                subcirc = QuantumCircuit(q)
                block_index_map = self._block_qargs_to_indices(block_qargs,
                                                               global_index_map)
                basis_count = 0
                for nd in block:
                    if nd.op.name == basis_gate_name:
                        basis_count += 1
                    subcirc.append(nd.op, [q[block_index_map[i]] for i in nd.qargs])
                unitary = UnitaryGate(Operator(subcirc))  # simulates the circuit
                if self.force_consolidate or unitary.num_qubits > 2 or \
                        self.decomposer.num_basis_gates(unitary) != basis_count:

                    new_dag.apply_operation_back(
                        unitary, sorted(block_qargs, key=lambda x: block_index_map[x]))
                else:
                    for nd in block:
                        new_dag.apply_operation_back(nd.op, nd.qargs, nd.cargs, nd.condition)

        return new_dag