    def op_RAISE_VARARGS(self, state, inst):
        if inst.arg == 0:
            exc = None
        elif inst.arg == 1:
            exc = state.pop()
        else:
            raise ValueError("Multiple argument raise is not supported.")
        state.append(inst, exc=exc)
        state.terminate()