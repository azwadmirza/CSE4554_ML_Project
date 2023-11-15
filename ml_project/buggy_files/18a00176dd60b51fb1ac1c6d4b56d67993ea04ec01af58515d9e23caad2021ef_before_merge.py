def _sort_translation_rule(c, *operands, dimension):
  out = xops.Sort(c, operands, dimension=dimension, is_stable=True)
  return out if len(operands) != 1 else xops.Tuple(c, [out])