def _subdiagrams(X, homology_dimensions, remove_dim=False):
    """For each diagram in a collection, extract the subdiagrams in a given
    list of homology dimensions. It is assumed that all diagrams in X contain
    the same number of points in each homology dimension."""
    n = len(X)
    if len(homology_dimensions) == 1:
        Xs = X[X[:, :, 2] == homology_dimensions[0]].reshape(n, -1, 3)
    else:
        Xs = np.concatenate([X[X[:, :, 2] == dim].reshape(n, -1, 3)
                             for dim in homology_dimensions],
                            axis=1)
    if remove_dim:
        Xs = Xs[:, :, :2]
    return Xs