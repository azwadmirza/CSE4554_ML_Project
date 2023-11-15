def lu_cpu_translation_rule(c, operand):
  shape = c.GetShape(operand)
  dtype = shape.element_type().type
  out = lapack.jax_getrf(c, operand)
  lu = c.GetTupleElement(out, 0)
  # Subtract 1 from the pivot to get 0-based indices.
  pivot = c.Sub(c.GetTupleElement(out, 1), c.ConstantS32Scalar(1))
  # Throw away the `info` value, because we have no way to report errors.
  return c.Tuple(lu, pivot)