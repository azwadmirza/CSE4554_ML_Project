def _broadcasting_shape_rule(name, *avals):
  shapes = onp.array([aval.shape for aval in avals if aval.shape])
  if not shapes.size:
    return ()
  if len({len(shape) for shape in shapes}) != 1:
    msg = '{} got arrays of different rank: {}.'
    raise TypeError(msg.format(name, ', '.join(map(str, map(tuple, shapes)))))
  result_shape = _try_broadcast_shapes(shapes)
  if result_shape is None:
    msg = '{} got incompatible shapes for broadcasting: {}.'
    raise TypeError(msg.format(name, ', '.join(map(str, map(tuple, shapes)))))
  return result_shape