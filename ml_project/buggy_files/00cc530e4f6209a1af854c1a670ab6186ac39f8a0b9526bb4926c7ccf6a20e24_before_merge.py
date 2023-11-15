def _check_shape(name, shape, *param_shapes):
  try:
    shape = tuple(map(int, shape))
  except TypeError as err:
    msg = "{} requires a concrete tuple of integers as shape argument, got {}."
    raise ValueError(msg.format(name, shape)) from err
  if param_shapes:
    shape_ = lax.broadcast_shapes(shape, *param_shapes)
    if shape != shape_:
      msg = ("{} parameter shapes must be broadcast-compatible with shape "
             "argument, and the result of broadcasting the shapes must equal "
             "the shape argument, but got result {} for shape argument {}.")
      raise ValueError(msg.format(name, shape_, shape))