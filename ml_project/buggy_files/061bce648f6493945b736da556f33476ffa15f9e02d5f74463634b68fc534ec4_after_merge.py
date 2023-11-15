def _brcast(x, *others):
  # Used in jvprules to make binop broadcasting explicit for transposability.
  # Requires shape info during jvp tracing, which isn't strictly necessary.
  # We don't need full numpy broadcasting, but otherwise the logic is the same
  # so we reuse the broadcast_shapes function after filtering out scalars.
  shapes = tuple(filter(None, map(onp.shape, (x,) + others)))
  shape = shapes and broadcast_shapes(*shapes)
  if onp.shape(x) != shape:
    return _brcast_to(x, shape)
  else:
    return x