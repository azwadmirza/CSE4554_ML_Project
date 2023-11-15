    def op_BREAK_LOOP(self, state, inst):
        # NOTE: bytecode removed since py3.8
        end = state.get_top_block('LOOP')['end']
        state.append(inst, end=end)
        state.pop_block()
        state.fork(pc=end)