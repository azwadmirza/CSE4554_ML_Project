  def _no_duplicate_dims(dims, name):
    if len(set(dims)) != len(dims):
      raise TypeError(f"{name} in scatter op must not repeat; got: {dims}.")