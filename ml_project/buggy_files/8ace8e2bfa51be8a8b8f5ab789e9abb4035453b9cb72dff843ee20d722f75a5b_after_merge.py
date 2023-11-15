def _static_idx(idx: slice, size: Union[int, Poly]):
  """Helper function to compute the static slice start/limit/stride values."""
  if _any(type(s) is Poly for s in (idx.start, idx.stop, idx.step, size)):
    start, stop, step = _polymorphic_slice_indices(idx, size)
  elif isinstance(size, int):
    start, stop, step = idx.indices(size)
  else:
    raise TypeError(size)

  if type(start) is not Poly and type(stop) is not Poly:
    if (step < 0 and stop >= start) or (step > 0 and start >= stop):
      return 0, 0, 1, False  # sliced to size zero

  if step > 0:
    return start, stop, step, False
  else:
    k  = (start - stop - 1) % (-step)
    return stop + k + 1, start + 1, -step, True