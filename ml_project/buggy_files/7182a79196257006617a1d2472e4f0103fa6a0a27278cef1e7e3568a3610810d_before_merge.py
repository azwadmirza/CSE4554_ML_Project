def silhouette_distances(diagrams_1, diagrams_2, sampling, step_size,
                         power=2., p=2., **kwargs):
    silhouette_1 = silhouettes(diagrams_1, sampling, power)
    if np.array_equal(diagrams_1, diagrams_2):
        unnorm_dist = squareform(pdist(silhouette_1, 'minkowski', p=p))
    else:
        silhouette_2 = silhouettes(diagrams_2, sampling, power)
        unnorm_dist = cdist(silhouette_1, silhouette_2, 'minkowski', p=p)
    return (step_size ** (1 / p)) * unnorm_dist