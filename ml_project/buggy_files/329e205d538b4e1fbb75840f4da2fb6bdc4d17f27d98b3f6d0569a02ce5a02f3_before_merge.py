    def _strip_phi_nodes(self, func_ir):
        """Strip Phi nodes from ``func_ir``

        For each phi node, put incoming value to their respective incoming
        basic-block at possibly the latest position (i.e. after the latest
        assignment to the corresponding variable).
        """
        exporters = defaultdict(list)
        phis = set()
        # Find all variables that needs to be exported
        for label, block in func_ir.blocks.items():
            for assign in block.find_insts(ir.Assign):
                if isinstance(assign.value, ir.Expr):
                    if assign.value.op == 'phi':
                        phis.add(assign)
                        phi = assign.value
                        for ib, iv in zip(phi.incoming_blocks,
                                          phi.incoming_values):
                            exporters[ib].append((assign.target, iv))

        # Rewrite the blocks with the new exporting assignments
        newblocks = {}
        for label, block in func_ir.blocks.items():
            newblk = copy(block)
            newblocks[label] = newblk

            # strip phis
            newblk.body = [stmt for stmt in block.body if stmt not in phis]

            # insert exporters
            for target, rhs in exporters[label]:
                if rhs is not ir.UNDEFINED:
                    assign = ir.Assign(
                        target=target,
                        value=rhs,
                        loc=target.loc
                    )
                    # Insert at the earliest possible location; i.e. after the
                    # last assignment to rhs
                    assignments = [stmt
                                   for stmt in newblk.find_insts(ir.Assign)
                                   if stmt.target == rhs]
                    if assignments:
                        last_assignment = assignments[-1]
                        newblk.insert_after(assign, last_assignment)
                    else:
                        newblk.prepend(assign)

        func_ir.blocks = newblocks
        return func_ir