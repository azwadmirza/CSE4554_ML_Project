def start_hyperopt_show(args: Dict[str, Any]) -> None:
    """
    Show details of a hyperopt epoch previously evaluated
    """
    from freqtrade.optimize.hyperopt import Hyperopt

    config = setup_utils_configuration(args, RunMode.UTIL_NO_EXCHANGE)

    filteroptions = {
        'only_best': config.get('hyperopt_list_best', False),
        'only_profitable': config.get('hyperopt_list_profitable', False),
        'filter_min_trades': config.get('hyperopt_list_min_trades', 0),
        'filter_max_trades': config.get('hyperopt_list_max_trades', 0),
        'filter_min_avg_time': config.get('hyperopt_list_min_avg_time', None),
        'filter_max_avg_time': config.get('hyperopt_list_max_avg_time', None),
        'filter_min_avg_profit': config.get('hyperopt_list_min_avg_profit', None),
        'filter_max_avg_profit': config.get('hyperopt_list_max_avg_profit', None),
        'filter_min_total_profit': config.get('hyperopt_list_min_total_profit', None),
        'filter_max_total_profit': config.get('hyperopt_list_max_total_profit', None)
    }
    no_header = config.get('hyperopt_show_no_header', False)

    trials_file = (config['user_data_dir'] /
                   'hyperopt_results' / 'hyperopt_results.pickle')

    # Previous evaluations
    trials = Hyperopt.load_previous_results(trials_file)
    total_epochs = len(trials)

    trials = _hyperopt_filter_trials(trials, filteroptions)
    trials_epochs = len(trials)

    n = config.get('hyperopt_show_index', -1)
    if n > trials_epochs:
        raise OperationalException(
                f"The index of the epoch to show should be less than {trials_epochs + 1}.")
    if n < -trials_epochs:
        raise OperationalException(
                f"The index of the epoch to show should be greater than {-trials_epochs - 1}.")

    # Translate epoch index from human-readable format to pythonic
    if n > 0:
        n -= 1

    print_json = config.get('print_json', False)

    if trials:
        val = trials[n]
        Hyperopt.print_epoch_details(val, total_epochs, print_json, no_header,
                                     header_str="Epoch details")