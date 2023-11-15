def canonicalize_dtype(dtype):
  """Convert from a dtype to a canonical dtype based on config.x64_enabled."""
  if isinstance(dtype, str) and dtype == "bfloat16":
    dtype = bfloat16
  try:
    dtype = np.dtype(dtype)
  except TypeError as e:
    raise TypeError(f'dtype {dtype!r} not understood') from e

  if config.x64_enabled:
    return dtype
  else:
    return _dtype_to_32bit_dtype.get(dtype, dtype)