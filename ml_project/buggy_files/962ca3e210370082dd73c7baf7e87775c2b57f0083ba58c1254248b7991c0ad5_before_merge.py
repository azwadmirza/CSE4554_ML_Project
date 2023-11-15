def persistence_image_distances(diagrams_1, diagrams_2, sampling, step_size,
                                weight_function=lambda x: x, sigma=1., p=2.,
                                **kwargs):
    sampling_ = np.copy(sampling.reshape((-1,)))
    weights = weight_function(sampling_ - sampling_[0])
    persistence_image_1 = persistence_images(diagrams_1, sampling_, step_size,
                                             weights, sigma).reshape(
                                                 diagrams_1.shape[0], -1)
    if np.array_equal(diagrams_1, diagrams_2):
        unnorm_dist = squareform(pdist(persistence_image_1, "minkowski", p=p))
        return (step_size ** (1 / p)) * unnorm_dist
    persistence_image_2 = persistence_images(diagrams_2, sampling_, step_size,
                                             weights, sigma,).reshape(
                                                 diagrams_2.shape[0], -1)
    unnorm_dist = cdist(persistence_image_1, persistence_image_2,
                        "minkowski", p=p)
    return (step_size ** (1 / p)) * unnorm_dist