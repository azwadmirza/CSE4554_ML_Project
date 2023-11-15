def _ids_to_words(ids, dictionary):
    """Convert an iterable of ids to their corresponding words using a dictionary.
    This function abstracts away the differences between the HashDictionary and the standard one.

    Args:
        ids: list of list of tuples, where each tuple contains (token_id, iterable of token_ids).
            This is the format returned by the topic_coherence.segmentation functions.
    """
    if not dictionary.id2token:  # may not be initialized in the standard gensim.corpora.Dictionary
        setattr(dictionary, 'id2token', {v: k for k, v in dictionary.token2id.items()})

    top_words = set()
    for word_id in ids:
        word = dictionary.id2token[word_id]
        if isinstance(word, set):
            top_words = top_words.union(word)
        else:
            top_words.add(word)

    return top_words