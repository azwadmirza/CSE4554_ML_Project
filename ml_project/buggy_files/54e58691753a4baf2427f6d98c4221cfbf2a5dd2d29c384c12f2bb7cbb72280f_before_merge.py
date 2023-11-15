def solve(a, b):
  a, b = _promote_arg_dtypes(np.asarray(a), np.asarray(b))
  a_shape = np.shape(a)
  b_shape = np.shape(b)
  a_ndims = len(a_shape)
  b_ndims = len(b_shape)
  if not (a_ndims >= 2 and a_shape[-1] == a_shape[-2] and
          (a_ndims == b_ndims or a_ndims == b_ndims + 1)):
    msg = ("The arguments to solve must have shapes a=[..., m, m] and "
           "b=[..., m, k] or b=[..., m]; got a={} and b={}")
    raise ValueError(msg.format(a_shape, b_shape))
  lu, pivots = lax_linalg.lu(a)
  dtype = lax.dtype(a)

  # TODO(phawkins): add unit_diagonal support to solve_triangular, use it here
  # instead of explicit masking of l.
  m = a_shape[-1]
  l = np.tril(lu, -1)[:, :m] + np.eye(m, m, dtype=dtype)

  # TODO(phawkins): triangular_solve only supports matrices on the RHS, so we
  # add a dummy dimension. Extend it to support vectors and simplify this.
  x = b if a_ndims == b_ndims else b[..., None]

  permutation = lax_linalg.lu_pivots_to_permutation(pivots, m)
  x = x[..., permutation, :]

  x = lax_linalg.triangular_solve(l, x, left_side=True, lower=True)
  x = lax_linalg.triangular_solve(lu, x, left_side=True, lower=False)

  return x[..., 0] if a_ndims != b_ndims else x