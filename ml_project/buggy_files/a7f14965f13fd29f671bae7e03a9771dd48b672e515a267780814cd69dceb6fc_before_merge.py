def lu_pivots_to_permutation(swaps, k):
  """Converts the pivots (row swaps) returned by LU to a permutation."""

  def body_fn(i, loop_carry):
    swaps, permutation = loop_carry
    j = swaps[i]
    x, y = np.ravel(permutation[i]), np.ravel(permutation[j])
    permutation = lax.dynamic_update_index_in_dim(permutation, y, i, axis=0)
    permutation = lax.dynamic_update_index_in_dim(permutation, x, j, axis=0)
    return swaps, permutation

  n, = np.shape(swaps)
  permutation = np.arange(k)
  _, permutation = lax.fori_loop(
      onp.array(0, onp.int32), onp.array(n, onp.int32), body_fn, (swaps, permutation))
  return permutation