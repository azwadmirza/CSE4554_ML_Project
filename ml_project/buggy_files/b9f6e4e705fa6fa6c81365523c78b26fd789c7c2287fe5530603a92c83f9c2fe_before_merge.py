def betti_amplitudes(diagrams, sampling, step_size, p=2., **kwargs):
    bcs = betti_curves(diagrams, sampling)
    return (step_size ** (1 / p)) * np.linalg.norm(bcs, axis=1, ord=p)