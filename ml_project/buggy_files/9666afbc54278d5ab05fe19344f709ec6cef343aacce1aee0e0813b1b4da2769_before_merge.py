  def byte_LOAD_METHOD(self, state, op):
    # We don't support this 3.7 opcode yet; simply don't crash.
    # TODO(rechen): Implement
    # https://docs.python.org/3/library/dis.html#opcode-LOAD_METHOD.
    unused_name = self.frame.f_code.co_names[op.arg]
    state, unused_self_obj = state.pop()
    return state