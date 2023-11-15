def iota(dtype: DType, size: int) -> Array:
  """Wraps XLA's `Iota
  <https://www.tensorflow.org/xla/operation_semantics#iota>`_
  operator.
  """
  size = size if type(size) is masking.Poly else int(size)
  shape = canonicalize_shape((size,))
  dtype = dtypes.canonicalize_dtype(dtype)
  lazy_expr = lazy.iota(dtype, shape[0])
  aval = ShapedArray(shape, dtype)
  return xla.DeviceArray(aval, None, lazy_expr, xla.DeviceConstant())