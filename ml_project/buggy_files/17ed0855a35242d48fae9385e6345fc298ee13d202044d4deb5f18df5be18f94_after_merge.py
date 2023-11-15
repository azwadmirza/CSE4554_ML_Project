def _is_sorted(dims, op_name, name):
  for i in range(1, len(dims)):
    if dims[i] < dims[i - 1]:
      raise TypeError(f"{name} in {op_name} op must be sorted; got {dims}")