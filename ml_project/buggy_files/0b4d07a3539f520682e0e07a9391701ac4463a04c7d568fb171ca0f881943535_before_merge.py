def _hyperopt_filter_trials(trials: List, only_best: bool, only_profitable: bool) -> List:
    """
    Filter our items from the list of hyperopt results
    """
    if only_best:
        trials = [x for x in trials if x['is_best']]
    if only_profitable:
        trials = [x for x in trials if x['results_metrics']['profit'] > 0]

    logger.info(f"{len(trials)} " +
                ("best " if only_best else "") +
                ("profitable " if only_profitable else "") +
                "epochs found.")

    return trials