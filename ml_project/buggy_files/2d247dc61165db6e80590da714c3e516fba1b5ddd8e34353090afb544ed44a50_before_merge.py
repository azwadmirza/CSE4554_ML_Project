def heats(diagrams, sampling, step_size, sigma):
    heats_ = np.zeros((diagrams.shape[0],
                       sampling.shape[0], sampling.shape[0]))

    diagrams[diagrams < sampling[0, 0]] = sampling[0, 0]
    diagrams[diagrams > sampling[-1, 0]] = sampling[-1, 0]
    diagrams = np.array((diagrams - sampling[0, 0]) / step_size, dtype=int)

    [_heat(heats_[i], sampled_diag, sigma)
        for i, sampled_diag in enumerate(diagrams)]

    heats_ = heats_ - np.transpose(heats_, (0, 2, 1))
    heats_ = np.rot90(heats_, k=1, axes=(1, 2))
    return heats_