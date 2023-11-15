def lu_pivots_to_permutation(swaps, m):
  """Converts the pivots (row swaps) returned by LU to a permutation.

  We build a permutation rather than applying `swaps` directly to the rows
  of a matrix because lax loops aren't differentiable.

  Args:
    swaps: an array of shape (..., k) of row swaps to perform
    m: the size of the output permutation. m should be >= k.
  Returns:
    An int32 array of shape (..., m).
  """
  assert len(swaps.shape) >= 1
  batch_dims = swaps.shape[:-1]
  k = swaps.shape[-1]

  def body_fn(i, permutation):
    j = swaps[..., i]
    iotas = np.ix_(*(lax.iota(np.int32, b) for b in batch_dims))
    x = permutation[..., i]
    y = permutation[iotas + (j,)]
    permutation = ops.index_update(permutation, ops.index[..., i], y)
    return ops.index_update(permutation, ops.index[iotas + (j,)], x)

  permutation = lax.broadcasted_iota(np.int32, batch_dims + (m,),
                                     len(batch_dims))
  return lax.fori_loop(
    onp.array(0, onp.int32), onp.array(k, onp.int32), body_fn, permutation)