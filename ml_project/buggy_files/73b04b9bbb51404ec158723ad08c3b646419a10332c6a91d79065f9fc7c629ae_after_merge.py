def _find_word_boudaries(bin_reps) -> list:
    """
    Find start and end location of each word.

    :param str bin_reps: binary representation of a text

    :return: list of tuples (start, end)
    :rtype: list[tuple(int, int)]
    """
    boundary = np.argwhere(bin_reps == 1).reshape(-1)
    start_idx = boundary
    end_idx = boundary[1:].tolist() + [bin_reps.shape[0]]

    return list(zip(start_idx, end_idx))