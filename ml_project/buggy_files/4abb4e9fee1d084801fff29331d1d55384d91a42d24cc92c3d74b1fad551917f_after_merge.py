  def byte_LOAD_FAST(self, state, op):
    """Load a local. Unlike LOAD_NAME, it doesn't fall back to globals."""
    name = self.frame.f_code.co_varnames[op.arg]
    try:
      state, val = self.load_local(state, name)
    except KeyError:
      val = self._name_error_or_late_annotation(name).to_variable(state.node)
    self.check_for_deleted(state, name, val)
    self.trace_opcode(op, name, val)
    return state.push(val)