def s_one_set(topics):
    """
    This function performs s_one_set segmentation on a list of topics.
    s_one_set segmentation is defined as: s_one_set = {(W', W*) | W' = {w_i}; w_i belongs to W; W* = W}
    Example:
        >>> topics = [np.array([9, 10, 7])
        >>> s_one_set(topics)
        [[(9, array([ 9, 10,  7])),
          (10, array([ 9, 10,  7])),
          (7, array([ 9, 10,  7]))]]

    Args:
        topics : list of topics obtained from an algorithm such as LDA. Is a list such as [array([ 9, 10, 11]), array([ 9, 10,  7]), ...]

    Returns:
        s_one_set : list of list of (W', W*) tuples for all unique topic ids.
    """
    s_one_set = []

    for top_words in topics:
        s_one_set_t = []
        for w_prime in top_words:
            s_one_set_t.append((w_prime, top_words))
        s_one_set.append(s_one_set_t)

    return s_one_set