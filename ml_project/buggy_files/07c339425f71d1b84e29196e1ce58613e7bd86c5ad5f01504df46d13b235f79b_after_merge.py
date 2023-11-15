  def byte_LOAD_NAME(self, state, op):
    """Load a name. Can be a local, global, or builtin."""
    name = self.frame.f_code.co_names[op.arg]
    try:
      state, val = self.load_local(state, name)
    except KeyError:
      try:
        state, val = self.load_global(state, name)
      except KeyError:
        try:
          if self._is_private(name):
            # Private names must be explicitly imported.
            self.trace_opcode(op, name, None)
            raise KeyError()
          state, val = self.load_builtin(state, name)
        except KeyError:
          if self._is_private(name) or not self.has_unknown_wildcard_imports:
            one_val = self._name_error_or_late_annotation(name)
          else:
            one_val = self.convert.unsolvable
          self.trace_opcode(op, name, None)
          return state.push(one_val.to_variable(state.node))
    self.check_for_deleted(state, name, val)
    self.trace_opcode(op, name, val)
    return state.push(val)