def heat_amplitudes(diagrams, sampling, step_size, sigma=0.1, p=2., **kwargs):
    # WARNING: `heats` modifies `diagrams` in place
    step_size_factor = step_size ** (2 / p)
    heats_ = heats(diagrams, sampling, step_size, sigma).\
        reshape(len(diagrams), -1)
    amplitudes = np.linalg.norm(heats_, axis=1, ord=p)
    amplitudes *= step_size_factor
    return amplitudes