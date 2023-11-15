def landscape_amplitudes(
        diagrams, sampling, step_size, p=2., n_layers=1, **kwargs
        ):
    step_size_factor = step_size ** (1 / p)
    ls = landscapes(diagrams, sampling, n_layers).\
        reshape(len(diagrams), -1)
    amplitudes = np.linalg.norm(ls, axis=1, ord=p)
    amplitudes *= step_size_factor
    return amplitudes