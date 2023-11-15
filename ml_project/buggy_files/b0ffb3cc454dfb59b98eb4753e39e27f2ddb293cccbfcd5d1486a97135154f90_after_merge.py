def _pred_bcast_select(c, pred, x, y, x_y_aval: core.AbstractValue):
  pred_shape = c.get_shape(pred).dimensions()
  x_shape = c.get_shape(x).dimensions()
  y_shape = c.get_shape(y).dimensions()
  assert x_shape == y_shape
  if x_y_aval is core.abstract_unit:
    return x
  elif x_y_aval is core.abstract_token:
    return xops.AfterAll(c, [x, y])
  else:
    assert pred_shape == x_shape[:len(pred_shape)] == y_shape[:len(pred_shape)]
    bcast_pred = xops.BroadcastInDim(pred, x_shape, list(range(len(pred_shape))))
    return xops.Select(bcast_pred, x, y)