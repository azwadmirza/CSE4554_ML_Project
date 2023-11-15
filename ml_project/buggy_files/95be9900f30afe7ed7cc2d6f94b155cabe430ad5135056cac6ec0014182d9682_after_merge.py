def _filter(X, filtered_homology_dimensions, cutoff):
    n = len(X)
    homology_dimensions = sorted(np.unique(X[0, :, 2]))
    unfiltered_homology_dimensions = [dim for dim in homology_dimensions if
                                      dim not in filtered_homology_dimensions]

    if len(unfiltered_homology_dimensions) == 0:
        Xuf = np.empty((n, 0, 3), dtype=X.dtype)
    else:
        Xuf = _subdiagrams(X, unfiltered_homology_dimensions)

    # Compute a global 2D cutoff mask once
    cutoff_mask = X[:, :, 1] - X[:, :, 0] > cutoff
    Xf = []
    for dim in filtered_homology_dimensions:
        # Compute a 2D mask for persistence pairs in dimension dim
        dim_mask = X[:, :, 2] == dim
        # Need the indices relative to X of persistence triples in dimension
        # dim surviving the cutoff
        indices = np.nonzero(np.logical_and(dim_mask, cutoff_mask))
        if not indices[0].size:
            Xdim = np.tile([0., 0., dim], (n, 1, 1))
        else:
            # A unique element k is repeated N times *consecutively* in
            # indices[0] iff there are exactly N valid persistence triples
            # in the k-th diagram
            unique, counts = np.unique(indices[0], return_counts=True)
            max_n_points = np.max(counts)
            # Make a global 2D array of all valid triples
            X_indices = X[indices]
            min_value = np.min(X_indices[:, 0])  # For padding
            # Initialise the array of filtered subdiagrams in dimension m
            Xdim = np.tile([min_value, min_value, dim], (n, max_n_points, 1))
            # Since repeated indices in indices[0] are consecutive and we know
            # the counts per unique index, we can fill the top portion of
            # each 2D array entry of Xdim with the filtered triples from the
            # corresponding entry of X
            Xdim[indices[0], _multirange(counts)] = X_indices
        Xf.append(Xdim)

    Xf.append(Xuf)
    Xf = np.concatenate(Xf, axis=1)
    return Xf