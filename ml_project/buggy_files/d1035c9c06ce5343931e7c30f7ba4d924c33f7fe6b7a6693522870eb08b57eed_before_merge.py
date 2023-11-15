def _quantile(a, q, axis, interpolation, keepdims):
  a = asarray(a)
  if axis is None:
    a = ravel(a)
    axis = 0
  elif isinstance(axis, tuple):
    raise NotImplementedError("Tuple values for axis are not implemented")
  else:
    axis = _canonicalize_axis(axis, ndim(a))

  q_ndim = ndim(q)
  if q_ndim > 1:
    raise ValueError("q must be have rank <= 1, got shape {}".format(shape(q)))

  q = asarray(q)

  if not issubdtype(a.dtype, floating) or not issubdtype(q.dtype, floating):
    msg = "q and a arguments to quantile must be of float type, got {} and {}"
    raise TypeError(msg.format(a.dtype, q.dtype))

  # Promote q to at least float32 for precise interpolation.
  q = lax.convert_element_type(q, promote_types(q.dtype, float32))

  a_shape = shape(a)
  a = lax.sort(a, dimension=axis)

  n = a_shape[axis]
  q = lax.mul(q, _constant_like(q, n - 1))
  low = lax.floor(q)
  high = lax.ceil(q)
  high_weight = lax.sub(q, low)
  low_weight = lax.sub(_constant_like(high_weight, 1), high_weight)

  low = lax.clamp(_constant_like(low, 0), low, _constant_like(low, n - 1))
  high = lax.clamp(_constant_like(high, 0), high, _constant_like(high, n - 1))
  low = lax.convert_element_type(low, int64)
  high = lax.convert_element_type(high, int64)

  slice_sizes = list(a_shape)
  slice_sizes[axis] = 1

  dnums = lax.GatherDimensionNumbers(
    offset_dims=tuple(range(
      q_ndim,
      len(a_shape) + q_ndim if keepdims else len(a_shape) + q_ndim - 1)),
    collapsed_slice_dims=() if keepdims else (axis,),
    start_index_map=(axis,))
  low = low[..., None]
  high = high[..., None]
  low_value = lax.gather(a, low, dimension_numbers=dnums,
                         slice_sizes=slice_sizes)
  high_value = lax.gather(a, high, dimension_numbers=dnums,
                          slice_sizes=slice_sizes)
  if q_ndim == 1:
    low_weight = lax.broadcast_in_dim(low_weight, low_value.shape,
                                      broadcast_dimensions=(0,))
    high_weight = lax.broadcast_in_dim(high_weight, high_value.shape,
                                      broadcast_dimensions=(0,))

  if interpolation == "linear":
    result = lax.add(lax.mul(low_value.astype(q.dtype), low_weight),
                     lax.mul(high_value.astype(q.dtype), high_weight))
  elif interpolation == "lower":
    result = low_value
  elif interpolation == "higher":
    result = high_value
  elif interpolation == "nearest":
    pred = lax.le(high_weight, _constant_like(high_weight, 0.5))
    result = lax.select(pred, low_value, high_value)
  elif interpolation == "midpoint":
    result = lax.mul(lax.add(low_value, high_value), _constant_like(low_value, 0.5))
  else:
    raise ValueError(f"interpolation={interpolation!r} not recognized")

  return lax.convert_element_type(result, a.dtype)