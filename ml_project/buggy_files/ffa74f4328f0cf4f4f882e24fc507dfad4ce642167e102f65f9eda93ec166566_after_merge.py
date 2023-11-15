def dtype_to_etype(dtype):
  """Convert from dtype to canonical etype (reading config.x64_enabled)."""
  return xla_client.dtype_to_etype(dtypes.canonicalize_dtype(dtype))