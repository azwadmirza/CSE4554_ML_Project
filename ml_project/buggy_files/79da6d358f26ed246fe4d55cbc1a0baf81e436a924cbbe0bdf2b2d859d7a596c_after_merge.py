def _normalize_index(index, axis_size):
  """Normalizes an index value in the range [-N, N) to the range [0, N)."""
  if type(axis_size) is Poly:
    return index + axis_size if index < 0 else index

  return lax.select(
    lax.lt(index, _constant_like(index, 0)),
    lax.add(index, _constant_like(index, axis_size)),
    index)