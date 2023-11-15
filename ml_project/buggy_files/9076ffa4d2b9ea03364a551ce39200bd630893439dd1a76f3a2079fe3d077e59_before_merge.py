def randn_func(vectorisation_idx):
    try:
        N = len(vectorisation_idx)
    except TypeError:
        N = int(vectorisation_idx)

    numbers = np.random.randn(N)
    if N == 1:
        return numbers[0]
    else:
        return numbers