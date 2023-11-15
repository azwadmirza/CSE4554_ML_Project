def _brcast(x, *others):
  # used in jvprules to make binop broadcasting explicit for transposability.
  # requires shape info during jvp tracing, which isn't strictly necessary.
  shapes = list(filter(None, map(onp.shape, (x,) + others)))
  shape = tuple(shapes and onp.max(shapes, axis=0))
  if onp.shape(x) != shape:
    return _brcast_to(x, shape)
  else:
    return x