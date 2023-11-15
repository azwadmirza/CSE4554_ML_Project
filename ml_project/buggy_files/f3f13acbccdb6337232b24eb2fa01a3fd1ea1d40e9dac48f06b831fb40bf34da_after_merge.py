    def op_SETUP_LOOP(self, state, inst):
        # NOTE: bytecode removed since py3.8
        state.push_block(
            state.make_block(
                kind='LOOP',
                end=inst.get_jump_target(),
            )
        )