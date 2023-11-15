  def byte_MAKE_FUNCTION(self, state, op):
    """Create a function and push it onto the stack."""
    if self.PY2:
      name = None
    else:
      assert self.PY3
      state, name_var = state.pop()
      name = abstract_utils.get_atomic_python_constant(name_var)
    state, code = state.pop()
    if self.python_version >= (3, 6):
      get_args = self._get_extra_function_args_3_6
    else:
      get_args = self._get_extra_function_args
    state, defaults, kw_defaults, annot, late_annot, free_vars = (
        get_args(state, op.arg))
    self._process_function_type_comment(op, annot, late_annot)
    # TODO(dbaum): Add support for per-arg type comments.
    # TODO(dbaum): Add support for variable type comments.
    globs = self.get_globals_dict()
    fn = self._make_function(name, state.node, code, globs, defaults,
                             kw_defaults, annotations=annot,
                             late_annotations=late_annot,
                             closure=free_vars)
    self.trace_opcode(op, name, fn)
    self.trace_functiondef(fn)
    return state.push(fn)