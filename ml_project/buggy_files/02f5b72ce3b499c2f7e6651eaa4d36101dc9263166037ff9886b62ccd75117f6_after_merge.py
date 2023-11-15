def cosine_similarity(segmented_topics, accumulator, topics, measure='nlr', gamma=1):
    """
    This function calculates the indirect cosine measure. Given context vectors
    u = V(W') and w = V(W*) for the word sets of a pair S_i = (W', W*) indirect
    cosine measure is computed as the cosine similarity between u and w.

    The formula used is:

        m_{sim}_{(m, \gamma)}(W', W*) = s_{sim}(\vec{V}^{\,}_{m,\gamma}(W'), \vec{V}^{\,}_{m,\gamma}(W*))

    where each vector:

        \vec{V}^{\,}_{m,\gamma}(W') = \Bigg \{{\sum_{w_{i} \in W'}^{ } m(w_{i}, w_{j})^{\gamma}}\Bigg \}_{j = 1,...,|W|}

    Args:

        segmented_topics : Output from the segmentation module of the segmented topics. Is a list of list of tuples.
        accumulator : Output from the probability_estimation module. Is an accumulator of word occurrences (see text_analysis module).
        topics : Topics obtained from the trained topic model.
        measure : String. Direct confirmation measure to be used. Supported values are "nlr" (normalized log ratio).
        gamma : Gamma value for computing W', W* vectors; default is 1.

    Returns:

        s_cos_sim : list of indirect cosine similarity measure for each topic.

    """
    context_vectors = ContextVectorComputer(measure, topics, accumulator, gamma)

    s_cos_sim = []
    for topic_words, topic_segments in zip(topics, segmented_topics):
        topic_words = tuple(topic_words)  # because tuples are hashable
        segment_sims = np.zeros(len(topic_segments))
        for i, (w_prime, w_star) in enumerate(topic_segments):
            w_prime_cv = context_vectors[w_prime, topic_words]
            w_star_cv = context_vectors[w_star, topic_words]
            segment_sims[i] = _cossim(w_prime_cv, w_star_cv)
        s_cos_sim.append(np.mean(segment_sims))

    return s_cos_sim