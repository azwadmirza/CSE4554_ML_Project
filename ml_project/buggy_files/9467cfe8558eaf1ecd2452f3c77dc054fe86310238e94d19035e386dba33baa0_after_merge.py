def cholesky_cpu_translation_rule(c, operand):
  shape = c.GetShape(operand)
  dtype = shape.element_type().type
  if len(shape.dimensions()) == 2 and dtype in _cpu_lapack_types:
    potrf_output = lapack.jax_potrf(c, operand, lower=True)
    result = c.GetTupleElement(potrf_output, 0)
    info = c.GetTupleElement(potrf_output, 1)
    return c.Select(c.Eq(info, c.ConstantS32Scalar(0)), result,
                    _nan_like(c, result))
  else:
    # Fall back to the HLO implementation for batched Cholesky decomposition or
    # unsupported types.
    # TODO(phawkins): support LAPACK primitives in batched mode.
    return c.Cholesky(operand)