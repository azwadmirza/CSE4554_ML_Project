def randn_func(vectorisation_idx):
    try:
        N = len(vectorisation_idx)
        return np.random.randn(N)
    except TypeError:
        # scalar value
        return np.random.randn()