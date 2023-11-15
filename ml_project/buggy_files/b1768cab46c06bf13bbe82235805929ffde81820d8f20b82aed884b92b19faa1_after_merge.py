def landscape_distances(
        diagrams_1, diagrams_2, sampling, step_size, p=2., n_layers=1,
        **kwargs
        ):
    step_size_factor = step_size ** (1 / p)
    n_samples_1, n_points_1 = diagrams_1.shape[:2]
    n_layers_1 = min(n_layers, n_points_1)
    if np.array_equal(diagrams_1, diagrams_2):
        ls_1 = landscapes(diagrams_1, sampling, n_layers_1).\
            reshape(n_samples_1, -1)
        distances = pdist(ls_1, "minkowski", p=p)
        distances *= step_size_factor
        return squareform(distances)
    n_samples_2, n_points_2 = diagrams_2.shape[:2]
    n_layers_2 = min(n_layers, n_points_2)
    n_layers = max(n_layers_1, n_layers_2)
    ls_1 = landscapes(diagrams_1, sampling, n_layers).\
        reshape(n_samples_1, -1)
    ls_2 = landscapes(diagrams_2, sampling, n_layers).\
        reshape(n_samples_2, -1)
    distances = cdist(ls_1, ls_2, "minkowski", p=p)
    distances *= step_size_factor
    return distances