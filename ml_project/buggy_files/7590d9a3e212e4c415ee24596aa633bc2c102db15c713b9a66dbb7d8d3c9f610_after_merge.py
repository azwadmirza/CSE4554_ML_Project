def persistence_image_amplitudes(
        diagrams, sampling, step_size, sigma=0.1, weight_function=np.ones_like,
        p=2., **kwargs
        ):
    # For persistence images, `sampling` is a tall matrix with two columns
    # (the first for birth and the second for persistence), and `step_size` is
    # a 2d array
    weights = weight_function(sampling[:, 1])
    step_sizes_factor = np.product(step_size) ** (1 / p)
    # WARNING: `persistence_images` modifies `diagrams` in place
    persistence_images_ = persistence_images(
        diagrams, sampling, step_size, sigma, weights
        ).reshape(len(diagrams), -1)
    amplitudes = np.linalg.norm(persistence_images_, axis=1, ord=p)
    amplitudes *= step_sizes_factor
    return amplitudes