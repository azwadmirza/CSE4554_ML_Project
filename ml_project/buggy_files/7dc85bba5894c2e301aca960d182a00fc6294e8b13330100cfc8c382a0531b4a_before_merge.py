def s_one_pre(topics):
    """
    This function performs s_one_pre segmentation on a list of topics.
    s_one_pre segmentation is defined as: s_one_pre = {(W', W*) | W' = {w_i};
                                                                  W* = {w_j}; w_i, w_j belongs to W; i > j}
    Example:

        >>> topics = [np.array([1, 2, 3]), np.array([4, 5, 6])]
        >>> s_one_pre(topics)
        [[(2, 1), (3, 1), (3, 2)], [(5, 4), (6, 4), (6, 5)]]

    Args:
    ----
    topics : list of topics obtained from an algorithm such as LDA. Is a list such as [array([ 9, 10, 11]), array([ 9, 10,  7]), ...]

    Returns:
    -------
    s_one_pre : list of list of (W', W*) tuples for all unique topic ids
    """
    s_one_pre = []

    for top_words in topics:
        s_one_pre_t = []
        for w_prime_index, w_prime in enumerate(top_words[1:]):
            for w_star in top_words[:w_prime_index + 1]:
                s_one_pre_t.append((w_prime, w_star))
        s_one_pre.append(s_one_pre_t)

    return s_one_pre