def heat_distances(diagrams_1, diagrams_2, sampling, step_size,
                   sigma=1., p=2., **kwargs):
    heat_1 = heats(diagrams_1, sampling, step_size, sigma).reshape(
        diagrams_1.shape[0], -1)
    if np.array_equal(diagrams_1, diagrams_2):
        unnorm_dist = squareform(pdist(heat_1, "minkowski", p=p))
        return (step_size ** (1 / p)) * unnorm_dist
    heat_2 = heats(diagrams_2, sampling, step_size, sigma).\
        reshape(diagrams_2.shape[0], -1)
    unnorm_dist = cdist(heat_1, heat_2, "minkowski", p=p)
    return (step_size ** (1 / p)) * unnorm_dist