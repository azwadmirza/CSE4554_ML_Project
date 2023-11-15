def silhouettes(diagrams, sampling, power, **kwargs):
    """Input: a batch of persistence diagrams with a sampling (3d array
    returned by _bin) of a one-dimensional range.
    """
    sampling = np.transpose(sampling, axes=(1, 2, 0))
    weights = np.diff(diagrams, axis=2)
    if power > 8.:
        weights = weights / np.max(weights, axis=1, keepdims=True)
    weights = weights ** power
    total_weights = np.sum(weights, axis=1)
    # Next line is a trick to avoid NaNs when computing `fibers_weighted_sum`
    total_weights[total_weights == 0.] = np.inf
    midpoints = (diagrams[:, :, [1]] + diagrams[:, :, [0]]) / 2.
    heights = (diagrams[:, :, [1]] - diagrams[:, :, [0]]) / 2.
    fibers = np.maximum(-np.abs(sampling - midpoints) + heights, 0)
    fibers_weighted_sum = np.sum(weights * fibers, axis=1) / total_weights
    return fibers_weighted_sum