  def _make_function(self, name, node, code, globs, defaults, kw_defaults,
                     closure=None, annotations=None):
    """Create a function or closure given the arguments."""
    if closure:
      closure = tuple(
          c for c in abstract_utils.get_atomic_python_constant(closure))
      log.info("closure: %r", closure)
    if not name:
      name = abstract_utils.get_atomic_python_constant(code).co_name
    if not name:
      name = "<lambda>"
    val = abstract.InterpreterFunction.make(
        name, code=abstract_utils.get_atomic_python_constant(code),
        f_locals=self.frame.f_locals, f_globals=globs,
        defaults=defaults, kw_defaults=kw_defaults,
        closure=closure, annotations=annotations, vm=self)
    # TODO(ampere): What else needs to be an origin in this case? Probably stuff
    # in closure.
    var = self.program.NewVariable()
    var.AddBinding(val, code.bindings, node)
    if val.signature.annotations:
      self.functions_type_params_check.append((val, self.frame.current_opcode))
    return var