def eig_cpu_translation_rule(c, operand):
  out = lapack.jax_geev(c, operand)
  return c.Tuple(c.GetTupleElement(out, 0), c.GetTupleElement(out, 1),
                 c.GetTupleElement(out, 2))