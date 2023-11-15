def silhouette_distances(
        diagrams_1, diagrams_2, sampling, step_size, power=1., p=2., **kwargs
        ):
    step_size_factor = step_size ** (1 / p)
    are_arrays_equal = np.array_equal(diagrams_1, diagrams_2)
    silhouettes_1 = silhouettes(diagrams_1, sampling, power)
    if are_arrays_equal:
        distances = pdist(silhouettes_1, 'minkowski', p=p)
        distances *= step_size_factor
        return squareform(distances)
    silhouettes_2 = silhouettes(diagrams_2, sampling, power)
    distances = cdist(silhouettes_1, silhouettes_2, 'minkowski', p=p)
    distances *= step_size_factor
    return distances