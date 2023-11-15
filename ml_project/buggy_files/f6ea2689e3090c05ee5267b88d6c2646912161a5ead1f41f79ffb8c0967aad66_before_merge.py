    def op_SETUP_WITH(self, state, inst):
        cm = state.pop()    # the context-manager
        state.push(cm)

        yielded = state.make_temp()
        state.push(yielded)
        state.append(inst, contextmanager=cm)

        state.push_block({
            'kind': 'with',
            'end': inst.get_jump_target(),
        })

        # Forces a new block
        state.fork(pc=inst.next)