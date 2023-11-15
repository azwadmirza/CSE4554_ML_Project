def _hyperopt_filter_trials(trials: List, filteroptions: dict) -> List:
    """
    Filter our items from the list of hyperopt results
    """
    if filteroptions['only_best']:
        trials = [x for x in trials if x['is_best']]
    if filteroptions['only_profitable']:
        trials = [x for x in trials if x['results_metrics']['profit'] > 0]
    if filteroptions['filter_min_trades'] > 0:
        trials = [
                    x for x in trials
                    if x['results_metrics']['trade_count'] > filteroptions['filter_min_trades']
                 ]
    if filteroptions['filter_max_trades'] > 0:
        trials = [
                    x for x in trials
                    if x['results_metrics']['trade_count'] < filteroptions['filter_max_trades']
                 ]
    if filteroptions['filter_min_avg_time'] is not None:
        trials = [x for x in trials if x['results_metrics']['trade_count'] > 0]
        trials = [
                    x for x in trials
                    if x['results_metrics']['duration'] > filteroptions['filter_min_avg_time']
                 ]
    if filteroptions['filter_max_avg_time'] is not None:
        trials = [x for x in trials if x['results_metrics']['trade_count'] > 0]
        trials = [
                    x for x in trials
                    if x['results_metrics']['duration'] < filteroptions['filter_max_avg_time']
                 ]
    if filteroptions['filter_min_avg_profit'] is not None:
        trials = [x for x in trials if x['results_metrics']['trade_count'] > 0]
        trials = [
                    x for x in trials
                    if x['results_metrics']['avg_profit']
                    > filteroptions['filter_min_avg_profit']
                 ]
    if filteroptions['filter_max_avg_profit'] is not None:
        trials = [x for x in trials if x['results_metrics']['trade_count'] > 0]
        trials = [
                    x for x in trials
                    if x['results_metrics']['avg_profit']
                    < filteroptions['filter_max_avg_profit']
                 ]
    if filteroptions['filter_min_total_profit'] is not None:
        trials = [x for x in trials if x['results_metrics']['trade_count'] > 0]
        trials = [
                    x for x in trials
                    if x['results_metrics']['profit'] > filteroptions['filter_min_total_profit']
                 ]
    if filteroptions['filter_max_total_profit'] is not None:
        trials = [x for x in trials if x['results_metrics']['trade_count'] > 0]
        trials = [
                    x for x in trials
                    if x['results_metrics']['profit'] < filteroptions['filter_max_total_profit']
                 ]

    logger.info(f"{len(trials)} " +
                ("best " if filteroptions['only_best'] else "") +
                ("profitable " if filteroptions['only_profitable'] else "") +
                "epochs found.")

    return trials