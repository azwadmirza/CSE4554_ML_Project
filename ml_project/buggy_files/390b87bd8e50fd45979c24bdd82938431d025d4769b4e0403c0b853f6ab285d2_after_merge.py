def betti_distances(
        diagrams_1, diagrams_2, sampling, step_size, p=2., **kwargs
        ):
    step_size_factor = step_size ** (1 / p)
    are_arrays_equal = np.array_equal(diagrams_1, diagrams_2)
    betti_curves_1 = betti_curves(diagrams_1, sampling)
    if are_arrays_equal:
        distances = pdist(betti_curves_1, "minkowski", p=p)
        distances *= step_size_factor
        return squareform(distances)
    betti_curves_2 = betti_curves(diagrams_2, sampling)
    distances = cdist(betti_curves_1, betti_curves_2, "minkowski", p=p)
    distances *= step_size_factor
    return distances