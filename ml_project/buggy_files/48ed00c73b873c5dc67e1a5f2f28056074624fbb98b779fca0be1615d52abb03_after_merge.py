def p_boolean_document(corpus, segmented_topics):
    """This function performs the boolean document probability estimation.
    Boolean document estimates the probability of a single word as the number
    of documents in which the word occurs divided by the total number of documents.

    Args:
        corpus : The corpus of documents.
        segmented_topics : Output from the segmentation of topics. Could be simply topics too.

    Returns:
        accumulator : word occurrence accumulator instance that can be used to lookup token
            frequencies and co-occurrence frequencies.
    """
    top_ids = unique_ids_from_segments(segmented_topics)
    return CorpusAccumulator(top_ids).accumulate(corpus)