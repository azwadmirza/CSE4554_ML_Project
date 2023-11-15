def silhouette_amplitudes(diagrams, sampling, step_size, power=2., p=2.,
                          **kwargs):
    sht = silhouettes(diagrams, sampling, power)
    return (step_size ** (1 / p)) * np.linalg.norm(sht, axis=1, ord=p)