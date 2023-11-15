def tensordot(a, b, axes=2):
  _check_arraylike("tensordot", a, b)
  if not (ndim(a) >= 1 and ndim(b) >= 1):
    msg = "tensordot requires a.ndim and b.dim to be at least 1, got {} and {}."
    raise TypeError(msg.format(ndim(a), ndim(b)))

  if type(axes) is int:
    a, b = _promote_dtypes(a, b)
    a_reshape = lax.reshape(a, (_prod(a.shape[:-axes]), _prod(a.shape[-axes:])))
    b_reshape = lax.reshape(b, (_prod(b.shape[:axes]), _prod(b.shape[axes:])))
    out_reshape = lax.dot(a_reshape, b_reshape)
    return lax.reshape(out_reshape, a.shape[:-axes] + b.shape[axes:])
  elif type(axes) in (list, tuple) and len(axes) == 2:
    ax1, ax2 = axes
    if type(ax1) == type(ax2) == int:
      a_transposed = moveaxis(a, ax1, -1) if ax1 != a.ndim - 1 else a
      b_transposed = moveaxis(b, ax2, 0) if ax2 != 0 else b
      return tensordot(a_transposed, b_transposed, 1)
    elif type(ax1) in (list, tuple) and type(ax2) in (list, tuple):
      if len(ax1) != len(ax2):
        msg = "tensordot requires axes lists to have equal length, got {} and {}."
        raise TypeError(msg.format(ax1, ax2))
      num_axes = len(ax1)
      a_transposed = moveaxis(a, ax1, tuple(range(a.ndim - num_axes, a.ndim)))
      b_transposed = moveaxis(b, ax2, tuple(range(num_axes)))
      return tensordot(a_transposed, b_transposed, num_axes)
  msg = ("tensordot axes argument must be an int, a pair of ints, or a pair of "
         "lists/tuples of ints.")
  raise TypeError(msg)