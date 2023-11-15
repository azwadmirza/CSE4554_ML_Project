  def byte_CALL_METHOD(self, state, op):
    # We don't support this 3.7 opcode yet; simply don't crash.
    # TODO(rechen): Implement
    # https://docs.python.org/3/library/dis.html#opcode-CALL_METHOD.
    for _ in range(op.arg):
      state = state.pop_and_discard()
    return state.push(self.new_unsolvable(state.node))