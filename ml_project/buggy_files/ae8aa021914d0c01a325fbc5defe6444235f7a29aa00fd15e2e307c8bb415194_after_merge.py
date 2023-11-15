def _build_laplacian(data, spacing, mask, beta, multichannel):
    l_x, l_y, l_z = data.shape[:3]
    edges = _make_graph_edges_3d(l_x, l_y, l_z)
    weights = _compute_weights_3d(data, spacing, beta=beta, eps=1.e-10,
                                  multichannel=multichannel)
    if mask is not None:
        # Remove edges of the graph connected to masked nodes, as well
        # as corresponding weights of the edges.
        mask0 = np.hstack([mask[..., :-1].ravel(), mask[:, :-1].ravel(),
                           mask[:-1].ravel()])
        mask1 = np.hstack([mask[..., 1:].ravel(), mask[:, 1:].ravel(),
                           mask[1:].ravel()])
        ind_mask = np.logical_and(mask0, mask1)
        edges, weights = edges[:, ind_mask], weights[ind_mask]

        # Reassign edges labels to 0, 1, ... edges_number - 1
        _, inv_idx = np.unique(edges, return_inverse=True)
        edges = inv_idx.reshape(edges.shape)

    # Build the sparse linear system
    pixel_nb = l_x * l_y * l_z
    i_indices = edges.ravel()
    j_indices = edges[::-1].ravel()
    data = np.hstack((weights, weights))
    lap = sparse.coo_matrix((data, (i_indices, j_indices)),
                            shape=(pixel_nb, pixel_nb))
    lap.setdiag(-np.ravel(lap.sum(axis=0)))
    return lap.tocsr()