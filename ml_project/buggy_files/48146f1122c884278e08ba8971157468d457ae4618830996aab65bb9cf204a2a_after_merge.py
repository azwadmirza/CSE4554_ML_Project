    def next(self, instruction, call=False):
        """
        Architecture-specific hook point for enhance_next.
        """
        if CS_GRP_CALL in instruction.groups:
            if not call:
                return None

        elif CS_GRP_JUMP not in instruction.groups:
            return None

        # At this point, all operands have been resolved.
        # Assume only single-operand jumps.
        if len(instruction.operands) != 1:
            return None

        # Memory operands must be dereferenced
        op   = instruction.operands[0]
        addr = op.int
        if addr:
            addr &= pwndbg.arch.ptrmask
        if op.type == CS_OP_MEM:
            if addr is None:
                addr = self.memory(instruction, op)

            # self.memory may return none, so we need to check it here again
            if addr is not None:
                try:
                    # fails with gdb.MemoryError if the dereferenced address
                    # doesn't belong to any of process memory maps
                    addr = int(pwndbg.memory.poi(pwndbg.typeinfo.ppvoid, addr))
                except gdb.MemoryError:
                    return None
        if op.type == CS_OP_REG:
            addr = self.register(instruction, op)

        # Evidently this can happen?
        if addr is None:
            return None

        return int(addr)