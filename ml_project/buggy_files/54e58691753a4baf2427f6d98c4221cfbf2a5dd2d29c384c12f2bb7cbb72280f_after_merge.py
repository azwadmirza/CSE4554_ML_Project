def solve(a, b):
  a, b = _promote_arg_dtypes(np.asarray(a), np.asarray(b))
  a_shape = np.shape(a)
  b_shape = np.shape(b)
  a_ndims = len(a_shape)
  b_ndims = len(b_shape)
  if not (a_ndims >= 2 and a_shape[-1] == a_shape[-2] and b_ndims >= 1):
    msg = ("The arguments to solve must have shapes a=[..., m, m] and "
           "b=[..., m, k] or b=[..., m]; got a={} and b={}")
    raise ValueError(msg.format(a_shape, b_shape))
  lu, pivots = lax_linalg.lu(a)
  dtype = lax.dtype(a)

  m = a_shape[-1]

  # Numpy treats the RHS as a (batched) vector if the number of dimensions
  # differ by 1. Otherwise, broadcasting rules apply.
  x = b[..., None] if a_ndims == b_ndims + 1 else b

  batch_dims = lax.broadcast_shapes(lu.shape[:-2], x.shape[:-2])
  x = np.broadcast_to(x, batch_dims + x.shape[-2:])
  lu = np.broadcast_to(lu, batch_dims + lu.shape[-2:])

  permutation = lax_linalg.lu_pivots_to_permutation(pivots, m)
  permutation = np.broadcast_to(permutation, batch_dims + (m,))
  iotas = np.ix_(*(lax.iota(np.int32, b) for b in batch_dims + (1,)))
  x = x[iotas[:-1] + (permutation, slice(None))]

  # TODO(phawkins): add unit_diagonal support to triangular_solve, use it here
  # instead of explicit masking of l.
  l = np.tril(lu, -1)[..., :, :m] + np.eye(m, m, dtype=dtype)
  x = lax_linalg.triangular_solve(l, x, left_side=True, lower=True)
  x = lax_linalg.triangular_solve(lu, x, left_side=True, lower=False)

  return x[..., 0] if a_ndims == b_ndims + 1 else x