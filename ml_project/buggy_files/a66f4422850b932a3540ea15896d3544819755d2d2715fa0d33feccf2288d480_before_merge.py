def heat_amplitudes(diagrams, sampling, step_size, sigma=1., p=2., **kwargs):
    heat = heats(diagrams, sampling, step_size, sigma)
    return np.linalg.norm(heat, axis=(1, 2), ord=p)