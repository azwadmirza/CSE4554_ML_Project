def silhouette_amplitudes(
        diagrams, sampling, step_size, power=1., p=2., **kwargs
        ):
    step_size_factor = step_size ** (1 / p)
    silhouettes_ = silhouettes(diagrams, sampling, power)
    amplitudes = np.linalg.norm(silhouettes_, axis=1, ord=p)
    amplitudes *= step_size_factor
    return amplitudes