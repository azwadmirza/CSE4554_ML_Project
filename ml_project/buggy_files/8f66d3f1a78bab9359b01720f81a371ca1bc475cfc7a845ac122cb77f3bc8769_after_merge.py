  def byte_MAKE_CLOSURE(self, state, op):
    """Make a function that binds local variables."""
    if self.PY2:
      # The py3 docs don't mention this change.
      name = None
    else:
      assert self.PY3
      state, name_var = state.pop()
      name = abstract_utils.get_atomic_python_constant(name_var)
    state, (closure, code) = state.popn(2)
    state, defaults, kw_defaults, annot, _ = (
        self._get_extra_function_args(state, op.arg))
    globs = self.get_globals_dict()
    fn = self._make_function(name, state.node, code, globs, defaults,
                             kw_defaults, annotations=annot, closure=closure)
    self.trace_functiondef(fn)
    return state.push(fn)