def heat_distances(
        diagrams_1, diagrams_2, sampling, step_size, sigma=0.1, p=2., **kwargs
        ):
    # WARNING: `heats` modifies `diagrams` in place
    step_size_factor = step_size ** (2 / p)
    are_arrays_equal = np.array_equal(diagrams_1, diagrams_2)
    heats_1 = heats(diagrams_1, sampling, step_size, sigma).\
        reshape(len(diagrams_1), -1)
    if are_arrays_equal:
        distances = pdist(heats_1, "minkowski", p=p)
        distances *= step_size_factor
        return squareform(distances)
    heats_2 = heats(diagrams_2, sampling, step_size, sigma).\
        reshape(len(diagrams_2), -1)
    distances = cdist(heats_1, heats_2, "minkowski", p=p)
    distances *= step_size_factor
    return distances