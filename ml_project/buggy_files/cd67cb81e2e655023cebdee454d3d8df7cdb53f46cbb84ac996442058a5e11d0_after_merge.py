def unique_ids_from_segments(segmented_topics):
    """Return the set of all unique ids in a list of segmented topics.

    Args:
        segmented_topics: list of tuples of (word_id_set1, word_id_set2). Each word_id_set
            is either a single integer, or a `numpy.ndarray` of integers.
    Returns:
        unique_ids : set of unique ids across all topic segments.
    """
    unique_ids = set()  # is a set of all the unique ids contained in topics.
    for s_i in segmented_topics:
        for word_id in itertools.chain.from_iterable(s_i):
            if hasattr(word_id, '__iter__'):
                unique_ids.update(word_id)
            else:
                unique_ids.add(word_id)

    return unique_ids