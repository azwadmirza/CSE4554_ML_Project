def _no_duplicate_dims(dims, op_name, name):
  if len(set(dims)) != len(dims):
    raise TypeError(f"{name} in {op_name} op must not repeat; got: {dims}.")