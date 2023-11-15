def svd_cpu_translation_rule(c, operand, full_matrices, compute_uv):
  shape = c.GetShape(operand)
  dtype = shape.element_type().type
  if len(shape.dimensions()) == 2 and dtype in _cpu_lapack_types:
    gesdd_out = lapack.jax_gesdd(c, operand, full_matrices=full_matrices,
                                 compute_uv=compute_uv)
    s = c.GetTupleElement(gesdd_out, 0)
    u = c.GetTupleElement(gesdd_out, 1)
    vt = c.GetTupleElement(gesdd_out, 2)
    ok = c.Eq(c.GetTupleElement(gesdd_out, 3), c.ConstantS32Scalar(0))
    s = _broadcasting_select(c, c.Reshape(ok, None, (1,)), s,
                             _nan_like(c, s))
    u = _broadcasting_select(c, c.Reshape(ok, None, (1, 1)), u,
                             _nan_like(c, u))
    vt = _broadcasting_select(c, c.Reshape(ok, None, (1, 1)), vt,
                              _nan_like(c, vt))
    return c.Tuple(s, u, vt)
  else:
    raise NotImplementedError(
        "Only unbatched singular value decomposition is implemented on CPU")