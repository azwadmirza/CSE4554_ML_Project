def betti_amplitudes(diagrams, sampling, step_size, p=2., **kwargs):
    step_size_factor = step_size ** (1 / p)
    bcs = betti_curves(diagrams, sampling)
    amplitudes = np.linalg.norm(bcs, axis=1, ord=p)
    amplitudes *= step_size_factor
    return amplitudes