    def op_END_FINALLY(self, state, inst):
        blk = state.pop_block()
        state.reset_stack(blk['entry_stack'])