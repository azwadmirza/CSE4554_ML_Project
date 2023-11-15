def _generate_hypercube(samples, dimensions, rng):
    """Returns distinct binary samples of length dimensions
    """
    if dimensions > 30:
        return np.hstack([_generate_hypercube(samples, dimensions - 30, rng),
                          _generate_hypercube(samples, 30, rng)])
    out = astype(sample_without_replacement(2 ** dimensions, samples,
                                            random_state=rng),
                 dtype='>u4', copy=False)
    out = np.unpackbits(out.view('>u1')).reshape((-1, 32))[:, -dimensions:]
    return out