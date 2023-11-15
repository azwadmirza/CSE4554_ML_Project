def _subdiagrams(X, homology_dimensions, remove_dim=False):
    """For each diagram in a collection, extract the subdiagrams in a given
    list of homology dimensions. It is assumed that all diagrams in X contain
    the same number of points in each homology dimension."""
    n_samples = len(X)
    X_0 = X[0]

    def _subdiagrams_single_homology_dimension(homology_dimension):
        n_features_in_dim = np.sum(X_0[:, 2] == homology_dimension)
        try:
            # In this case, reshape ensures copy
            Xs = X[X[:, :, 2] == homology_dimension].\
                reshape(n_samples, n_features_in_dim, 3)
            return Xs
        except ValueError as e:
            if e.args[0].lower().startswith("cannot reshape array"):
                raise ValueError(
                    f"All persistence diagrams in the collection must have "
                    f"the same number of birth-death-dimension triples in any "
                    f"given homology dimension. This is not true in homology "
                    f"dimension {homology_dimension}. Trivial triples for "
                    f"which birth = death may be added or removed to fulfill "
                    f"this requirement."
                )
            else:
                raise e

    if len(homology_dimensions) == 1:
        Xs = _subdiagrams_single_homology_dimension(homology_dimensions[0])
    else:
        # np.concatenate will also create a copy
        Xs = np.concatenate(
            [_subdiagrams_single_homology_dimension(dim)
             for dim in homology_dimensions],
            axis=1
            )
    if remove_dim:
        Xs = Xs[:, :, :2]
    return Xs