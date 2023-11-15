def _broadcasting_shape_rule(name, *avals):
  shapes = onp.array([aval.shape for aval in avals if aval.shape])
  if not shapes.size:
    return ()
  if len({len(shape) for shape in shapes}) != 1:
    msg = '{} got arrays of different rank: {}.'
    raise TypeError(msg.format(name, ', '.join(map(str, map(tuple, shapes)))))
  is_zero = onp.any(shapes == 0, axis=0)
  max_shape = onp.max(shapes, axis=0)
  result_shape = onp.where(is_zero, 0, max_shape)
  if not onp.all((shapes == result_shape) | (shapes == 1)):
    msg = '{} got incompatible shapes for broadcasting: {}.'
    raise TypeError(msg.format(name, ', '.join(map(str, map(tuple, shapes)))))
  return tuple(result_shape)