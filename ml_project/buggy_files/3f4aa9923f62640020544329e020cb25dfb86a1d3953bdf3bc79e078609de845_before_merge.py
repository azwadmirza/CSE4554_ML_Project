    def _indirect_jump_encountered(self, addr, cfg_node, irsb, func_addr, stmt_idx=DEFAULT_STATEMENT):
        """
        Called when we encounter an indirect jump. We will try to resolve this indirect jump using timeless (fast)
        indirect jump resolvers. If it cannot be resolved, we will see if this indirect jump has been resolved before.

        :param int addr:                Address of the block containing the indirect jump.
        :param cfg_node:                The CFGNode instance of the block that contains the indirect jump.
        :param pyvex.IRSB irsb:         The IRSB instance of the block that contains the indirect jump.
        :param int func_addr:           Address of the current function.
        :param int or str stmt_idx:     ID of the source statement.

        :return:    A 3-tuple of (whether it is resolved or not, all resolved targets, an IndirectJump object
                    if there is one or None otherwise)
        :rtype:     tuple
        """

        jumpkind = irsb.jumpkind
        l.debug('IRSB %#x has an indirect jump (%s) as its default exit.', addr, jumpkind)

        # try resolving it fast
        resolved, resolved_targets = self._resolve_indirect_jump_timelessly(addr, irsb, func_addr, jumpkind)
        if resolved:
            l.debug("Indirect jump at block %#x is resolved by a timeless indirect jump resolver. "
                    "%d targets found.", addr, len(resolved_targets))
            return True, resolved_targets, None

        l.debug("Indirect jump at block %#x cannot be resolved by a timeless indirect jump resolver.", addr)

        # Add it to our set. Will process it later if user allows.
        # Create an IndirectJump instance
        if addr not in self.indirect_jumps:
            if self.project.arch.branch_delay_slot:
                if len(cfg_node.instruction_addrs) < 2:
                    # sanity check
                    # decoding failed when decoding the second instruction (or even the first instruction)
                    return False, [ ], None
                ins_addr = cfg_node.instruction_addrs[-2]
            else:
                ins_addr = cfg_node.instruction_addrs[-1]
            ij = IndirectJump(addr, ins_addr, func_addr, jumpkind, stmt_idx, resolved_targets=[])
            self.indirect_jumps[addr] = ij
            resolved = False
        else:
            ij = self.indirect_jumps[addr]  # type: IndirectJump
            resolved = len(ij.resolved_targets) > 0

        return resolved, ij.resolved_targets, ij