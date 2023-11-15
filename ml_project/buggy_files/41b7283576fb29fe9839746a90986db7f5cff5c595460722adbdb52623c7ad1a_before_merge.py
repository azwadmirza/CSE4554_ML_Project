def iota(dtype: DType, size: int) -> Array:
  """Wraps XLA's `Iota
  <https://www.tensorflow.org/xla/operation_semantics#iota>`_
  operator.
  """
  size = int(size)
  dtype = dtypes.canonicalize_dtype(dtype)
  lazy_expr = lazy.iota(dtype, size)
  aval = ShapedArray((size,), dtype)
  return xla.DeviceArray(aval, None, lazy_expr, xla.DeviceConstant())