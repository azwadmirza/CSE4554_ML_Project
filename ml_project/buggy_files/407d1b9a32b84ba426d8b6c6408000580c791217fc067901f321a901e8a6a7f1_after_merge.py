def instBwith(data, fs, fk):
    """
    Instantaneous bandwidth of a signal.

    Computes the instantaneous bandwidth of the given data which can be
    windowed or not. The instantaneous bandwidth is determined by the time
    derivative of the envelope normalized by the envelope of the input data.

    :type data: :class:`~numpy.ndarray`
    :param data: Data to determine instantaneous bandwidth of.
    :param fs: Sampling frequency.
    :param fk: Filter coefficients for computing time derivative.
    :return: **sigma[, dsigma]** - Instantaneous bandwidth of input data, Time
        derivative of instantaneous bandwidth (windowed only).
    """
    x = envelope(data)
    if (size(x[1].shape) > 1):
        sigma = np.zeros(x[1].shape[0], dtype=np.float64)
        i = 0
        for row in x[1]:
            # faster alternative to calculate A_win_add
            A_win_add = np.hstack(
                ([row[0]] * (np.size(fk) // 2), row,
                 [row[np.size(row) - 1]] * (np.size(fk) // 2)))
            t = signal.lfilter(fk, 1, A_win_add)
            # t = t[size(fk) // 2:(size(t) - size(fk) // 2)]
            # correct start and end values
            t = t[size(fk) - 1:size(t)]
            sigma_win = abs((t * fs) / (row * 2 * pi))
            sigma[i] = np.median(sigma_win)
            i = i + 1
        # faster alternative to calculate sigma_add
        sigma_add = np.hstack(
            ([sigma[0]] * (np.size(fk) // 2), sigma,
             [sigma[np.size(sigma) - 1]] * (np.size(fk) // 2)))
        dsigma = signal.lfilter(fk, 1, sigma_add)
        # dsigma = dsigma[size(fk) // 2:(size(dsigma) - size(fk) // 2)]
        # correct start and end values
        dsigma = dsigma[size(fk) - 1:size(dsigma)]
        return sigma, dsigma
    else:
        row = x[1]
        sigma = np.zeros(size(x[0]), dtype=np.float64)
        # faster alternative to calculate A_win_add
        A_win_add = np.hstack(
            ([row[0]] * (np.size(fk) // 2), row,
             [row[np.size(row) - 1]] * (np.size(fk) // 2)))
        t = signal.lfilter(fk, 1, A_win_add)
        # correct start and end values
        t = t[size(fk) - 1:size(t)]
        sigma = abs((t * fs) / (x[1] * 2 * pi))
        return sigma