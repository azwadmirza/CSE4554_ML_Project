  def _eval_expr_as_tuple(self, node, expr):
    """Evaluate an expression as a tuple."""
    if not expr:
      return ()

    f_globals, f_locals = self.vm.frame.f_globals, self.vm.frame.f_locals
    result = abstract_utils.get_atomic_value(
        abstract_utils.eval_expr(self.vm, node, f_globals, f_locals, expr))
    # If the result is a tuple, expand it.
    if (isinstance(result, mixin.PythonConstant) and
        isinstance(result.pyval, tuple)):
      return tuple(abstract_utils.get_atomic_value(x) for x in result.pyval)
    else:
      return (result,)