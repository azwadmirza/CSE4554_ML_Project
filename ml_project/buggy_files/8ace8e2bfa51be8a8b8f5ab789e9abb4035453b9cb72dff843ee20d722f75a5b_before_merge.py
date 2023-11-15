def _static_idx(idx, size):
  """Helper function to compute the static slice start/limit/stride values."""
  assert isinstance(idx, slice)
  start, stop, step = idx.indices(size)
  if (step < 0 and stop >= start) or (step > 0 and start >= stop):
    return 0, 0, 1, False  # sliced to size zero

  if step > 0:
    return start, stop, step, False
  else:
    k  = (start - stop - 1) % (-step)
    return stop + k + 1, start + 1, -step, True