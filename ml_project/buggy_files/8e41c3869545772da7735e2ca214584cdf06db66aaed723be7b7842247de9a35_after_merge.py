    def num_connected_components(self, unitary_only=False):
        """How many non-entangled subcircuits can the circuit be factored to.

        Args:
            unitary_only (bool): Compute only unitary part of graph.

        Returns:
            int: Number of connected components in circuit.
        """
        # Convert registers to ints (as done in depth).
        reg_offset = 0
        reg_map = {}

        if unitary_only:
            regs = self.qregs
        else:
            regs = self.qregs+self.cregs

        for reg in regs:
            reg_map[reg.name] = reg_offset
            reg_offset += reg.size
        # Start with each qubit or cbit being its own subgraph.
        sub_graphs = [[bit] for bit in range(reg_offset)]

        num_sub_graphs = len(sub_graphs)

        # Here we are traversing the gates and looking to see
        # which of the sub_graphs the gate joins together.
        for instr, qargs, cargs in self.data:
            if unitary_only:
                args = qargs
                num_qargs = len(args)
            else:
                args = qargs+cargs
                num_qargs = len(args) + (1 if instr.control else 0)

            if num_qargs >= 2 and instr.name not in ['barrier', 'snapshot']:
                graphs_touched = []
                num_touched = 0
                # Controls necessarily join all the cbits in the
                # register that they use.
                if instr.control and not unitary_only:
                    creg = instr.control[0]
                    creg_int = reg_map[creg.name]
                    for coff in range(creg.size):
                        temp_int = creg_int+coff
                        for k in range(num_sub_graphs):
                            if temp_int in sub_graphs[k]:
                                graphs_touched.append(k)
                                num_touched += 1
                                break

                for item in args:
                    reg_int = reg_map[item[0].name]+item[1]
                    for k in range(num_sub_graphs):
                        if reg_int in sub_graphs[k]:
                            if k not in graphs_touched:
                                graphs_touched.append(k)
                                num_touched += 1
                                break

                # If the gate touches more than one subgraph
                # join those graphs together and return
                # reduced number of subgraphs
                if num_touched > 1:
                    connections = []
                    for idx in graphs_touched:
                        connections.extend(sub_graphs[idx])
                    _sub_graphs = []
                    for idx in range(num_sub_graphs):
                        if idx not in graphs_touched:
                            _sub_graphs.append(sub_graphs[idx])
                    _sub_graphs.append(connections)
                    sub_graphs = _sub_graphs
                    num_sub_graphs -= (num_touched-1)
            # Cannot go lower than one so break
            if num_sub_graphs == 1:
                break
        return num_sub_graphs