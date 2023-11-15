  def _eval_expr_as_tuple(self, node, f_globals, f_locals, expr):
    """Evaluate an expression as a tuple."""
    if not expr:
      return ()

    result = abstract_utils.get_atomic_value(
        abstract_utils.eval_expr(self.vm, node, f_globals, f_locals, expr))
    # If the result is a tuple, expand it.
    if (isinstance(result, mixin.PythonConstant) and
        isinstance(result.pyval, tuple)):
      return tuple(abstract_utils.get_atomic_value(x) for x in result.pyval)
    else:
      return (result,)