  def _reduce_prod_tree(x, axis=0):
    """Reduce by repeatedly splitting the array and multiplying."""
    while x.shape[axis] > 1:
      n = x.shape[axis]
      n1 = (n + 1) // 2
      n2 = n - n1
      x1 = slice_in_dim(x, 0, n1)
      x2 = slice_in_dim(x, n1, None)
      if n2 != n1:
        paddings = [(0, 0, 0)] * len(x.shape)
        paddings[axis] = (0, 1, 0)
        x2 = pad(x2, _const(x, 1), paddings)
      x = x1 * x2
    shape = list(x.shape)
    del shape[axis]
    return reshape(x, shape)