  def body_fn(i, permutation):
    j = swaps[..., i]
    iotas = np.ix_(*(lax.iota(np.int32, b) for b in batch_dims))
    x = permutation[..., i]
    y = permutation[iotas + (j,)]
    permutation = ops.index_update(permutation, ops.index[..., i], y)
    return ops.index_update(permutation, ops.index[iotas + (j,)], x)