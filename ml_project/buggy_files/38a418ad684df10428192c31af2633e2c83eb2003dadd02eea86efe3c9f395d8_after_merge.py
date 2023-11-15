def _result_type_raw(*args):
  if len(args) == 1:
    return _jax_type(args[0])
  return _least_upper_bound(*{_jax_type(arg) for arg in args})