  def _sorted_dims_in_range(dims, rank, name):
    if len(dims) == 0:
      return
    invalid_dim = None
    if dims[0] < 0:
      invalid_dim = dims[0]
    elif dims[-1] >= rank:
      invalid_dim = dims[-1]
    if invalid_dim:
      raise TypeError(f"Invalid {name} set in scatter op; valid range is "
                      f"[0, {rank}); got: {invalid_dim}.")