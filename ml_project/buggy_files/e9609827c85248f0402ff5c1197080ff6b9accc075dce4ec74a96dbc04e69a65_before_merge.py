def start_list_strategies(args: Dict[str, Any]) -> None:
    """
    Print Strategies available in a directory
    """
    config = setup_utils_configuration(args, RunMode.UTIL_NO_EXCHANGE)

    directory = Path(config.get('strategy_path', config['user_data_dir'] / USERPATH_STRATEGY))
    strategies = StrategyResolver.search_all_objects(directory)
    # Sort alphabetically
    strategies = sorted(strategies, key=lambda x: x['name'])
    strats_to_print = [{'name': s['name'], 'location': s['location'].name} for s in strategies]

    if args['print_one_column']:
        print('\n'.join([s['name'] for s in strategies]))
    else:
        print(tabulate(strats_to_print, headers='keys', tablefmt='pipe'))