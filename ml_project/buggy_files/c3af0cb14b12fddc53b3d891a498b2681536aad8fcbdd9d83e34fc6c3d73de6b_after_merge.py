def lu_cpu_translation_rule(c, operand):
  shape = c.GetShape(operand)
  batch_dims = shape.dimensions()[:-2]
  getrf_out = lapack.jax_getrf(c, operand)
  lu = c.GetTupleElement(getrf_out, 0)
  # Subtract 1 from the pivot to get 0-based indices.
  pivot = c.Sub(c.GetTupleElement(getrf_out, 1), c.ConstantS32Scalar(1))
  ok = c.Eq(c.GetTupleElement(getrf_out, 2), c.ConstantS32Scalar(0))
  lu = _broadcasting_select(c, c.Reshape(ok, None, batch_dims + (1, 1)), lu,
                            _nan_like(c, lu))
  return c.Tuple(lu, pivot)