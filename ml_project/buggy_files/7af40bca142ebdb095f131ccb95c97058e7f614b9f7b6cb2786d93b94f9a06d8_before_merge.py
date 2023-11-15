def broadcast_to(arr, shape):
  """Like Numpy's broadcast_to but doesn't necessarily return views."""
  arr = arr if isinstance(arr, ndarray) else array(arr)
  shape = tuple(map(int, shape))  # check that shape is concrete
  arr_shape = _shape(arr)
  if arr_shape == shape:
    return arr
  else:
    nlead = len(shape) - len(arr_shape)
    compatible = onp.equal(arr_shape, shape[nlead:]) | onp.equal(arr_shape, 1)
    if nlead < 0 or not onp.all(compatible):
      msg = "Incompatible shapes for broadcasting: {} and requested shape {}"
      raise ValueError(msg.format(arr_shape, shape))
    diff, = onp.where(onp.not_equal(shape[nlead:], arr_shape))
    new_dims = tuple(range(nlead)) + tuple(nlead + diff)
    kept_dims = tuple(onp.delete(onp.arange(len(shape)), new_dims))
    return lax.broadcast_in_dim(squeeze(arr, diff), shape, kept_dims)