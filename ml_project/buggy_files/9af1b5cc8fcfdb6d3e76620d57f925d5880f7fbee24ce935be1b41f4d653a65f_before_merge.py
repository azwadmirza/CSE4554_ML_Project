def _check_solve_shapes(a, b):
  if not (a.ndim >= 2 and a.shape[-1] == a.shape[-2] and b.ndim >= 1):
    msg = ("The arguments to solve must have shapes a=[..., m, m] and "
           "b=[..., m, k] or b=[..., m]; got a={} and b={}")
    raise ValueError(msg.format(a.shape, b.shape))