def summarize_corpus(corpus, ratio=0.2):
    """
    Returns a list of the most important documents of a corpus using a
    variation of the TextRank algorithm.
    The input must have at least INPUT_MIN_LENGTH (%d) documents for the
    summary to make sense.

    The length of the output can be specified using the ratio parameter,
    which determines how many documents will be chosen for the summary
    (defaults at 20%% of the number of documents of the corpus).

    The most important documents are returned as a list sorted by the
    document score, highest first.
    """ % INPUT_MIN_LENGTH
    hashable_corpus = _build_hasheable_corpus(corpus)

    # If the corpus is empty, the function ends.
    if len(corpus) == 0:
        logger.warning("Input corpus is empty.")
        return

    # Warns the user if there are too few documents.
    if len(corpus) < INPUT_MIN_LENGTH:
        logger.warning("Input corpus is expected to have at least %d documents.", INPUT_MIN_LENGTH)

    graph = _build_graph(hashable_corpus)
    _set_graph_edge_weights(graph)
    _remove_unreachable_nodes(graph)

    # Cannot calculate eigenvectors if number of unique words in text < 3. Warns user to add more text. The function ends.
    if len(graph.nodes()) < 3:
        logger.warning("Please add more sentences to the text. The number of reachable nodes is below 3")
        return

    pagerank_scores = _pagerank(graph)

    hashable_corpus.sort(key=lambda doc: pagerank_scores.get(doc, 0), reverse=True)

    return [list(doc) for doc in hashable_corpus[:int(len(corpus) * ratio)]]