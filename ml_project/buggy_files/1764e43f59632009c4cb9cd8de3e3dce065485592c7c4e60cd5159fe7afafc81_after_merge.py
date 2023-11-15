def compute_stats(ref_sample: str, raw_sample: str) -> dict:
    """
    Compute statistics for tokenization quality

    These statistics includes:

    **Character-Level**:
      True Positive, False Positive, True Negative, False Negative, Precision, Recall, and f1
    **Word-Level**:
      Precision, Recall, and f1
    **Other**:
      - Correct tokenization indicator: {0, 1} sequence indicating the correspoding
        word is tokenized correctly.

    :param str ref_sample: ground truth samples
    :param str samples samples that we want to evaluate

    :return: metrics in character and word-level and correctly tokenized word indicators
    :rtype: dict[str, float | str]
    """
    ref_sample = _binary_representation(ref_sample)
    sample = _binary_representation(raw_sample)

    # Compute charater-level statistics
    c_pos_pred, c_neg_pred = np.argwhere(sample == 1), np.argwhere(sample == 0)

    c_pos_pred = c_pos_pred[c_pos_pred < ref_sample.shape[0]]
    c_neg_pred = c_neg_pred[c_neg_pred < ref_sample.shape[0]]

    c_tp = np.sum(ref_sample[c_pos_pred] == 1)
    c_fp = np.sum(ref_sample[c_pos_pred] == 0)

    c_tn = np.sum(ref_sample[c_neg_pred] == 0)
    c_fn = np.sum(ref_sample[c_neg_pred] == 1)

    c_precision = c_tp / (c_tp + c_fp)
    c_recall = c_tp / (c_tp + c_fn)
    c_f1 = _f1(c_precision, c_recall)

    # Compute word-level statistics

    # Find correctly tokenized words in the reference sample
    word_boundaries = _find_word_boudaries(ref_sample)

    # Find correctly tokenized words in the sample
    ss_boundaries = _find_word_boudaries(sample)
    tokenization_indicators = _find_words_correctly_tokenised(
        word_boundaries, ss_boundaries
    )

    correctly_tokenised_words = np.sum(tokenization_indicators)

    w_precision = correctly_tokenised_words / np.sum(sample)
    w_recall = correctly_tokenised_words / np.sum(ref_sample)
    w_f1 = _f1(w_precision, w_recall)

    tokenization_indicators = list(
        map(lambda x: str(x), tokenization_indicators)
    )

    return {
        "char_level": {
            "tp": c_tp,
            "fp": c_fp,
            "tn": c_tn,
            "fn": c_fn,
            "precision": c_precision,
            "recall": c_recall,
            "f1": c_f1,
        },
        "word_level": {
            "precision": w_precision,
            "recall": w_recall,
            "f1": w_f1,
        },
        "global": {
            "tokenisation_indicators": "".join(tokenization_indicators)
        },
    }