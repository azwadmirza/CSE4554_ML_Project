    def op_POP_BLOCK(self, state, inst):
        blk = state.pop_block()
        if blk['kind'] == BlockKind('TRY'):
            state.append(inst, kind='try')
        # Forces a new block
        state.fork(pc=inst.next)