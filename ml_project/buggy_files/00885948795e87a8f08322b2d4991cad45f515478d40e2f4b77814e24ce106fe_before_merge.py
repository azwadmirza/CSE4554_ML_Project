def svd_cpu_translation_rule(c, operand, full_matrices, compute_uv):
  shape = c.GetShape(operand)
  dtype = shape.element_type().type
  if len(shape.dimensions()) == 2 and dtype in _cpu_lapack_types:
    out = lapack.jax_gesdd(c, operand, full_matrices=full_matrices, compute_uv=compute_uv)
    return c.Tuple(c.GetTupleElement(out, 0),
                   c.GetTupleElement(out, 1),
                   c.GetTupleElement(out, 2))
  else:
    raise NotImplementedError(
        "Only unbatched singular value decomposition is implemented on CPU")