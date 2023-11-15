def _calculate_permutation_scores(estimator, X, y, col_idx, random_state,
                                  n_repeats, scorer):
    """Calculate score when `col_idx` is permuted."""
    original_feature = _safe_column_indexing(X, col_idx).copy()
    temp = original_feature.copy()

    scores = np.zeros(n_repeats)
    for n_round in range(n_repeats):
        random_state.shuffle(temp)
        _safe_column_setting(X, col_idx, temp)
        feature_score = scorer(estimator, X, y)
        scores[n_round] = feature_score

    _safe_column_setting(X, col_idx, original_feature)
    return scores