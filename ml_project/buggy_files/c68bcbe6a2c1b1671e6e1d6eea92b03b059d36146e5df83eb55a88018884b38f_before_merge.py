def matrix_to_tril_vec(x, diagonal=0):
    idxs = onp.tril_indices(x.shape[-1], diagonal)
    return x[..., idxs[0], idxs[1]]