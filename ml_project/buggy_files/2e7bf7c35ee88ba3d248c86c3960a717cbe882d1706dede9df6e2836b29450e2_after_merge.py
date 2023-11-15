    def dump(self, instruction):
        """
        Debug-only method.
        """
        ins = instruction
        rv  = []
        rv.append('%s %s' % (ins.mnemonic, ins.op_str))

        for i, group in enumerate(ins.groups):
            rv.append('   groups[%i]   = %s' % (i, groups.get(group, group)))

        rv.append('           next = %#x' % (ins.next))
        rv.append('      condition = %r' % (ins.condition))

        for i, op in enumerate(ins.operands):
            rv.append('   operands[%i] = %s' % (i, ops.get(op.type, op.type)))
            rv.append('       access   = %s' % (access.get(op.access, op.access)))

            if op.int is not None:
                rv.append('            int = %#x' % (op.int))
            if op.symbol is not None:
                rv.append('            sym = %s' % (op.symbol))
            if op.str is not None:
                rv.append('            str = %s' % (op.str))

        return '\n'.join(rv)