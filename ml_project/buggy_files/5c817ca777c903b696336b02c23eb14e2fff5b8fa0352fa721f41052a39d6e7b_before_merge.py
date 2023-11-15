def start_hyperopt_list(args: Dict[str, Any]) -> None:
    """
    List hyperopt epochs previously evaluated
    """
    from freqtrade.optimize.hyperopt import Hyperopt

    config = setup_utils_configuration(args, RunMode.UTIL_NO_EXCHANGE)

    only_best = config.get('hyperopt_list_best', False)
    only_profitable = config.get('hyperopt_list_profitable', False)
    print_colorized = config.get('print_colorized', False)
    print_json = config.get('print_json', False)
    no_details = config.get('hyperopt_list_no_details', False)
    no_header = False

    trials_file = (config['user_data_dir'] /
                   'hyperopt_results' / 'hyperopt_results.pickle')

    # Previous evaluations
    trials = Hyperopt.load_previous_results(trials_file)
    total_epochs = len(trials)

    trials = _hyperopt_filter_trials(trials, only_best, only_profitable)

    # TODO: fetch the interval for epochs to print from the cli option
    epoch_start, epoch_stop = 0, None

    if print_colorized:
        colorama_init(autoreset=True)

    try:
        # Human-friendly indexes used here (starting from 1)
        for val in trials[epoch_start:epoch_stop]:
            Hyperopt.print_results_explanation(val, total_epochs, not only_best, print_colorized)

    except KeyboardInterrupt:
        print('User interrupted..')

    if trials and not no_details:
        sorted_trials = sorted(trials, key=itemgetter('loss'))
        results = sorted_trials[0]
        Hyperopt.print_epoch_details(results, total_epochs, print_json, no_header)