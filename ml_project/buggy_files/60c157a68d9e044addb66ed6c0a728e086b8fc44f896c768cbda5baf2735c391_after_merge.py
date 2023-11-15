def eigh_cpu_translation_rule(c, operand, lower):
  shape = c.GetShape(operand)
  batch_dims = shape.dimensions()[:-2]
  syevd_out = lapack.jax_syevd(c, operand, lower=lower)
  v = c.GetTupleElement(syevd_out, 0)
  w = c.GetTupleElement(syevd_out, 1)
  ok = c.Eq(c.GetTupleElement(syevd_out, 2), c.ConstantS32Scalar(0))
  v = _broadcasting_select(c, c.Reshape(ok, None, batch_dims + (1, 1)), v,
                           _nan_like(c, v))
  w = _broadcasting_select(c, c.Reshape(ok, None, batch_dims + (1,)), w,
                           _nan_like(c, w))
  return c.Tuple(v, w)