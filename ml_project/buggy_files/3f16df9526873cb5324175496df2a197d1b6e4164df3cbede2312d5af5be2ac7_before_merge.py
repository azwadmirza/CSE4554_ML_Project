def _find_words_correctly_tokenised(
        ref_boundaries: list,
        predicted_boundaries: list
    ) -> tuple:
    """
    Find whether each word is correctly tokenized

    :param list[tuple(int, int)] ref_boundaries: word boundaries of reference tokenization
    :param list[tuple(int, int)] predicted_boundaries: word boundareies of predicted tokenization

    :return: binary sequence where 1 indicates the corresponding word is tokenized correctly
    :rtype: tuple[int] 
    """

    ref_b = dict(zip(ref_boundaries, [1]*len(ref_boundaries)))

    labels = tuple(map(lambda x: ref_b.get(x, 0), predicted_boundaries))
    return labels