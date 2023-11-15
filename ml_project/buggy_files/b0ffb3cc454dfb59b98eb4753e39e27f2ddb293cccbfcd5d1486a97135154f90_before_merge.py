def _pred_bcast_select(c, pred, x, y):
  pred_shape = c.get_shape(pred).dimensions()
  x_shape = c.get_shape(x).dimensions()
  y_shape = c.get_shape(y).dimensions()
  assert x_shape == y_shape
  if not c.get_shape(x).is_array() and not c.get_shape(y).is_array():
    # Two tokens
    return xops.AfterAll(c, [x, y])
  else:
    assert pred_shape == x_shape[:len(pred_shape)] == y_shape[:len(pred_shape)]
    bcast_pred = xops.BroadcastInDim(pred, x_shape, list(range(len(pred_shape))))
    return xops.Select(bcast_pred, x, y)