def eig_cpu_translation_rule(c, operand):
  shape = c.GetShape(operand)
  batch_dims = shape.dimensions()[:-2]
  geev_out = lapack.jax_geev(c, operand)
  w = c.GetTupleElement(geev_out, 0)
  vl = c.GetTupleElement(geev_out, 1)
  vr = c.GetTupleElement(geev_out, 2)
  ok = c.Eq(c.GetTupleElement(geev_out, 3), c.ConstantS32Scalar(0))
  w = _broadcasting_select(c, c.Reshape(ok, None, batch_dims + (1,)), w,
                           _nan_like(c, w))
  vl = _broadcasting_select(c, c.Reshape(ok, None, batch_dims + (1, 1)), vl,
                            _nan_like(c, vl))
  vr = _broadcasting_select(c, c.Reshape(ok, None, batch_dims + (1, 1)), vr,
                            _nan_like(c, vr))
  return c.Tuple(w, vl, vr)