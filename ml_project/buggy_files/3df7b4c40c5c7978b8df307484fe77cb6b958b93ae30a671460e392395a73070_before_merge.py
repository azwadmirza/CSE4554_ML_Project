def rand_func(vectorisation_idx):
    try:
        N = len(vectorisation_idx)
    except TypeError:
        N = int(vectorisation_idx)

    numbers = np.random.rand(N)
    if N == 1:
        return numbers[0]
    else:
        return numbers