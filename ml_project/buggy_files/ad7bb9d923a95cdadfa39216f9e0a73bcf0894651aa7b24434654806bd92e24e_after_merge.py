def log_conditional_probability(segmented_topics, accumulator):
    """
    This function calculates the log-conditional-probability measure
    which is used by coherence measures such as U_mass.
    This is defined as: m_lc(S_i) = log[(P(W', W*) + e) / P(W*)]

    Args:
        segmented_topics : Output from the segmentation module of the segmented topics.
            Is a list of list of tuples.
        accumulator: word occurrence accumulator from probability_estimation.

    Returns:
        m_lc : List of log conditional probability measure for each topic.
    """
    m_lc = []
    num_docs = float(accumulator.num_docs)
    for s_i in segmented_topics:
        segment_sims = []
        for w_prime, w_star in s_i:
            try:
                w_star_count = accumulator[w_star]
                co_occur_count = accumulator[w_prime, w_star]
                m_lc_i = np.log(((co_occur_count / num_docs) + EPSILON) / (w_star_count / num_docs))
            except KeyError:
                m_lc_i = 0.0

            segment_sims.append(m_lc_i)
        m_lc.append(np.mean(segment_sims))

    return m_lc