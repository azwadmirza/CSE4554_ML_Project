def persistence_image_distances(
        diagrams_1, diagrams_2, sampling, step_size, sigma=0.1,
        weight_function=np.ones_like, p=2., **kwargs
        ):
    # For persistence images, `sampling` is a tall matrix with two columns
    # (the first for birth and the second for persistence), and `step_size` is
    # a 2d array
    weights = weight_function(sampling[:, 1])
    step_sizes_factor = np.product(step_size) ** (1 / p)
    # WARNING: `persistence_images` modifies `diagrams` in place
    are_arrays_equal = np.array_equal(diagrams_1, diagrams_2)
    persistence_images_1 = \
        persistence_images(diagrams_1, sampling, step_size, sigma, weights).\
        reshape(len(diagrams_1), -1)
    if are_arrays_equal:
        distances = pdist(persistence_images_1, "minkowski", p=p)
        distances *= step_sizes_factor
        return squareform(distances)
    persistence_images_2 = persistence_images(
        diagrams_2, sampling, step_size, sigma, weights
        ).reshape(len(diagrams_2), -1)
    distances = cdist(
        persistence_images_1, persistence_images_2, "minkowski", p=p
        )
    distances *= step_sizes_factor
    return distances