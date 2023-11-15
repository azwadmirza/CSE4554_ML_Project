    def op_END_FINALLY(self, state, inst):
        state.append(inst)
        # actual bytecode has stack_effect of -6
        # we don't emulate the exact stack behavior
        state.pop()     # unsure but seems to work
        state.pop()     # unsure but seems to work