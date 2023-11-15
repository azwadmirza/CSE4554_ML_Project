def eigh_cpu_translation_rule(c, operand, lower):
  out = lapack.jax_syevd(c, operand, lower=lower)
  return c.Tuple(c.GetTupleElement(out, 0), c.GetTupleElement(out, 1))