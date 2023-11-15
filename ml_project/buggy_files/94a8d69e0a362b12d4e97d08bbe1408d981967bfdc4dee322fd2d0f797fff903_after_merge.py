def _get_max_identity(dtype):
  if onp.issubdtype(dtype, onp.floating):
    return onp.array(-onp.inf, dtype)
  elif onp.issubdtype(dtype, onp.integer):
    return onp.array(onp.iinfo(dtype).min, dtype)
  elif onp.issubdtype(dtype, onp.bool_):
    return onp.array(False, onp.bool_)