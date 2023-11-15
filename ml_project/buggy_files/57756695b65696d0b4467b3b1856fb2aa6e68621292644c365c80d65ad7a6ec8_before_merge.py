    def op_BEGIN_FINALLY(self, state, inst):
        res = state.make_temp()  # unused
        state.push(res)
        state.append(inst, state=res)