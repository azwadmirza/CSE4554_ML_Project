  def byte_CALL_METHOD(self, state, op):
    state, args = state.popn(op.arg)
    state, func = state.pop()
    state, result = self.call_function_with_state(state, func, args)
    return state.push(result)