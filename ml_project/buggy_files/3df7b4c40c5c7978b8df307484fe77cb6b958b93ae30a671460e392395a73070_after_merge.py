def rand_func(vectorisation_idx):
    try:
        N = len(vectorisation_idx)
        return np.random.rand(N)
    except TypeError:
        # scalar value
        return np.random.rand()