    def depth(self):
        """Return circuit depth (i.e. length of critical path).
        This does not include compiler or simulator directives
        such as 'barrier' or 'snapshot'.

        Returns:
            int: Depth of circuit.

        Notes:
            The circuit depth and the DAG depth need not bt the
            same.
        """
        # Labels the registers by ints
        # and then the qubit position in
        # a register is given by reg_int+qubit_num
        reg_offset = 0
        reg_map = {}
        for reg in self.qregs+self.cregs:
            reg_map[reg.name] = reg_offset
            reg_offset += reg.size

        # A list that holds the height of each qubit
        # and classical bit.
        op_stack = [0]*reg_offset
        # Here we are playing a modified version of
        # Tetris where we stack gates, but multi-qubit
        # gates, or measurements have a block for each
        # qubit or cbit that are connected by a virtual
        # line so that they all stacked at the same depth.
        # Conditional gates act on all cbits in the register
        # they are conditioned on.
        # We do not consider barriers or snapshots as
        # They are transpiler and simulator directives.
        # The max stack height is the circuit depth.
        for instr, qargs, cargs in self.data:
            if instr.name not in ['barrier', 'snapshot']:
                levels = []
                reg_ints = []
                for ind, reg in enumerate(qargs+cargs):
                    # Add to the stacks of the qubits and
                    # cbits used in the gate.
                    reg_ints.append(reg_map[reg[0].name]+reg[1])
                    levels.append(op_stack[reg_ints[ind]] + 1)
                if instr.control:
                    # Controls operate over all bits in the
                    # classical register they use.
                    cint = reg_map[instr.control[0].name]
                    for off in range(instr.control[0].size):
                        if cint+off not in reg_ints:
                            reg_ints.append(cint+off)
                            levels.append(op_stack[cint+off]+1)

                max_level = max(levels)
                for ind in reg_ints:
                    op_stack[ind] = max_level
        return max(op_stack)