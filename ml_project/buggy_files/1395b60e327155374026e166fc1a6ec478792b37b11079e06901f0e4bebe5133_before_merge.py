  def body_fn(i, loop_carry):
    swaps, permutation = loop_carry
    j = swaps[i]
    x, y = np.ravel(permutation[i]), np.ravel(permutation[j])
    permutation = lax.dynamic_update_index_in_dim(permutation, y, i, axis=0)
    permutation = lax.dynamic_update_index_in_dim(permutation, x, j, axis=0)
    return swaps, permutation