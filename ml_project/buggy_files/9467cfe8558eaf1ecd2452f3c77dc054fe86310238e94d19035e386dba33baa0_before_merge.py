def cholesky_cpu_translation_rule(c, operand):
  shape = c.GetShape(operand)
  dtype = shape.element_type().type
  if len(shape.dimensions()) == 2 and dtype in _cpu_lapack_types:
    return c.GetTupleElement(lapack.jax_potrf(c, operand, lower=True), 0)
  else:
    # Fall back to the HLO implementation for batched Cholesky decomposition or
    # unsupported types.
    # TODO(phawkins): support LAPACK primitives in batched mode.
    return c.Cholesky(operand)