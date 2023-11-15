def start_list_strategies(args: Dict[str, Any]) -> None:
    """
    Print files with Strategy custom classes available in the directory
    """
    config = setup_utils_configuration(args, RunMode.UTIL_NO_EXCHANGE)

    directory = Path(config.get('strategy_path', config['user_data_dir'] / USERPATH_STRATEGIES))
    strategy_objs = StrategyResolver.search_all_objects(directory, not args['print_one_column'])
    # Sort alphabetically
    strategy_objs = sorted(strategy_objs, key=lambda x: x['name'])

    if args['print_one_column']:
        print('\n'.join([s['name'] for s in strategy_objs]))
    else:
        _print_objs_tabular(strategy_objs, config.get('print_colorized', False))