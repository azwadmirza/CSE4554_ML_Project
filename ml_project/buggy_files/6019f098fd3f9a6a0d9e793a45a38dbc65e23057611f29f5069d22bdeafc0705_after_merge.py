    def op_RAISE_VARARGS(self, state, inst):
        in_exc_block = any([
            state.get_top_block("EXCEPT") is not None,
            state.get_top_block("FINALLY") is not None
        ])
        if inst.arg == 0:
            exc = None
            if in_exc_block:
                raise UnsupportedError(
                    "The re-raising of an exception is not yet supported.",
                    loc=self.get_debug_loc(inst.lineno),
                )
        elif inst.arg == 1:
            exc = state.pop()
        else:
            raise ValueError("Multiple argument raise is not supported.")
        state.append(inst, exc=exc)
        state.terminate()