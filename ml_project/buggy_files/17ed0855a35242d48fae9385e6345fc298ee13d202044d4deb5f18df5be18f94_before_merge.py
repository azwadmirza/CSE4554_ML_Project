  def _is_sorted(dims, name):
    for i in range(1, len(dims)):
      if dims[i] < dims[i - 1]:
        raise TypeError(f"{name} in scatter op must be sorted; got {dims}")