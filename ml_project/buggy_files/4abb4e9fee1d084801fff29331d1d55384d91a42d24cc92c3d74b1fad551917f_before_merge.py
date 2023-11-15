  def byte_LOAD_FAST(self, state, op):
    """Load a local. Unlike LOAD_NAME, it doesn't fall back to globals."""
    name = self.frame.f_code.co_varnames[op.arg]
    try:
      state, val = self.load_local(state, name)
    except KeyError:
      self.errorlog.name_error(self.frames, name)
      val = self.new_unsolvable(state.node)
    self.check_for_deleted(state, name, val)
    self.trace_opcode(op, name, val)
    return state.push(val)