    def op_SETUP_WITH(self, state, inst):
        cm = state.pop()    # the context-manager

        yielded = state.make_temp()
        state.append(inst, contextmanager=cm)

        state.push_block(
            state.make_block(
                kind='WITH_FINALLY',
                end=inst.get_jump_target(),
            )
        )

        state.push(cm)
        state.push(yielded)

        state.push_block(
            state.make_block(
                kind='WITH',
                end=inst.get_jump_target(),
            )
        )
        # Forces a new block
        state.fork(pc=inst.next)