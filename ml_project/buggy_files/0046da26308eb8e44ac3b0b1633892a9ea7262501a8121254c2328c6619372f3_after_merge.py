def s_one_one(topics):
    """
    This function performs s_one_one segmentation on a list of topics.
    s_one_one segmentation is defined as: s_one_one = {(W', W*) | W' = {w_i}; W* = {w_j}; w_i, w_j belongs to W; i != j}
    Example:

        >>> topics = [np.array([1, 2, 3]), np.array([4, 5, 6])]
        >>> s_one_pre(topics)
        [[(1, 2), (1, 3), (2, 1), (2, 3), (3, 1), (3, 2)], [(4, 5), (4, 6), (5, 4), (5, 6), (6, 4), (6, 5)]]

    Args:
        topics : list of topics obtained from an algorithm such as LDA. Is a list such as [array([ 9, 10, 11]), array([ 9, 10,  7]), ...]

    Returns:
        s_one_one : list of list of (W', W*) tuples for all unique topic ids
    """
    s_one_one = []

    for top_words in topics:
        s_one_one_t = []
        for w_prime_index, w_prime in enumerate(top_words):
            for w_star_index, w_star in enumerate(top_words):
                if w_prime_index == w_star_index:
                    continue
                else:
                    s_one_one_t.append((w_prime, w_star))
        s_one_one.append(s_one_one_t)

    return s_one_one