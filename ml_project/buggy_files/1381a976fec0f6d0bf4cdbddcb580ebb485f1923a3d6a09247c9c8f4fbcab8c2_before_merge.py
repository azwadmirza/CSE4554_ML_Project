    def _build_subcommands(self) -> None:
        """
        Builds and attaches all subcommands.
        :return: None
        """
        # Build shared arguments (as group Common Options)
        _common_parser = argparse.ArgumentParser(add_help=False)
        group = _common_parser.add_argument_group("Common arguments")
        self._build_args(optionlist=ARGS_COMMON, parser=group)

        _strategy_parser = argparse.ArgumentParser(add_help=False)
        strategy_group = _strategy_parser.add_argument_group("Strategy arguments")
        self._build_args(optionlist=ARGS_STRATEGY, parser=strategy_group)

        # Build main command
        self.parser = argparse.ArgumentParser(description='Free, open source crypto trading bot')
        self._build_args(optionlist=['version'], parser=self.parser)

        from freqtrade.commands import (start_create_userdir, start_download_data,
                                        start_hyperopt_list, start_hyperopt_show,
                                        start_list_exchanges, start_list_markets,
                                        start_list_strategies, start_new_hyperopt,
                                        start_new_strategy, start_list_timeframes,
                                        start_plot_dataframe, start_plot_profit,
                                        start_backtesting, start_hyperopt, start_edge,
                                        start_test_pairlist, start_trading)

        subparsers = self.parser.add_subparsers(dest='command',
                                                # Use custom message when no subhandler is added
                                                # shown from `main.py`
                                                # required=True
                                                )

        # Add trade subcommand
        trade_cmd = subparsers.add_parser('trade', help='Trade module.',
                                          parents=[_common_parser, _strategy_parser])
        trade_cmd.set_defaults(func=start_trading)
        self._build_args(optionlist=ARGS_TRADE, parser=trade_cmd)

        # Add backtesting subcommand
        backtesting_cmd = subparsers.add_parser('backtesting', help='Backtesting module.',
                                                parents=[_common_parser, _strategy_parser])
        backtesting_cmd.set_defaults(func=start_backtesting)
        self._build_args(optionlist=ARGS_BACKTEST, parser=backtesting_cmd)

        # Add edge subcommand
        edge_cmd = subparsers.add_parser('edge', help='Edge module.',
                                         parents=[_common_parser, _strategy_parser])
        edge_cmd.set_defaults(func=start_edge)
        self._build_args(optionlist=ARGS_EDGE, parser=edge_cmd)

        # Add hyperopt subcommand
        hyperopt_cmd = subparsers.add_parser('hyperopt', help='Hyperopt module.',
                                             parents=[_common_parser, _strategy_parser],
                                             )
        hyperopt_cmd.set_defaults(func=start_hyperopt)
        self._build_args(optionlist=ARGS_HYPEROPT, parser=hyperopt_cmd)

        # add create-userdir subcommand
        create_userdir_cmd = subparsers.add_parser('create-userdir',
                                                   help="Create user-data directory.",
                                                   )
        create_userdir_cmd.set_defaults(func=start_create_userdir)
        self._build_args(optionlist=ARGS_CREATE_USERDIR, parser=create_userdir_cmd)

        # add new-strategy subcommand
        build_strategy_cmd = subparsers.add_parser('new-strategy',
                                                   help="Create new strategy")
        build_strategy_cmd.set_defaults(func=start_new_strategy)
        self._build_args(optionlist=ARGS_BUILD_STRATEGY, parser=build_strategy_cmd)

        # add new-hyperopt subcommand
        build_hyperopt_cmd = subparsers.add_parser('new-hyperopt',
                                                   help="Create new hyperopt")
        build_hyperopt_cmd.set_defaults(func=start_new_hyperopt)
        self._build_args(optionlist=ARGS_BUILD_HYPEROPT, parser=build_hyperopt_cmd)

        # Add list-strategies subcommand
        list_strategies_cmd = subparsers.add_parser(
            'list-strategies',
            help='Print available strategies.',
            parents=[_common_parser],
        )
        list_strategies_cmd.set_defaults(func=start_list_strategies)
        self._build_args(optionlist=ARGS_LIST_STRATEGIES, parser=list_strategies_cmd)

        # Add list-exchanges subcommand
        list_exchanges_cmd = subparsers.add_parser(
            'list-exchanges',
            help='Print available exchanges.',
            parents=[_common_parser],
        )
        list_exchanges_cmd.set_defaults(func=start_list_exchanges)
        self._build_args(optionlist=ARGS_LIST_EXCHANGES, parser=list_exchanges_cmd)

        # Add list-timeframes subcommand
        list_timeframes_cmd = subparsers.add_parser(
            'list-timeframes',
            help='Print available ticker intervals (timeframes) for the exchange.',
            parents=[_common_parser],
        )
        list_timeframes_cmd.set_defaults(func=start_list_timeframes)
        self._build_args(optionlist=ARGS_LIST_TIMEFRAMES, parser=list_timeframes_cmd)

        # Add list-markets subcommand
        list_markets_cmd = subparsers.add_parser(
            'list-markets',
            help='Print markets on exchange.',
            parents=[_common_parser],
        )
        list_markets_cmd.set_defaults(func=partial(start_list_markets, pairs_only=False))
        self._build_args(optionlist=ARGS_LIST_PAIRS, parser=list_markets_cmd)

        # Add list-pairs subcommand
        list_pairs_cmd = subparsers.add_parser(
            'list-pairs',
            help='Print pairs on exchange.',
            parents=[_common_parser],
        )
        list_pairs_cmd.set_defaults(func=partial(start_list_markets, pairs_only=True))
        self._build_args(optionlist=ARGS_LIST_PAIRS, parser=list_pairs_cmd)

        # Add test-pairlist subcommand
        test_pairlist_cmd = subparsers.add_parser(
            'test-pairlist',
            help='Test your pairlist configuration.',
        )
        test_pairlist_cmd.set_defaults(func=start_test_pairlist)
        self._build_args(optionlist=ARGS_TEST_PAIRLIST, parser=test_pairlist_cmd)

        # Add download-data subcommand
        download_data_cmd = subparsers.add_parser(
            'download-data',
            help='Download backtesting data.',
            parents=[_common_parser],
        )
        download_data_cmd.set_defaults(func=start_download_data)
        self._build_args(optionlist=ARGS_DOWNLOAD_DATA, parser=download_data_cmd)

        # Add Plotting subcommand
        plot_dataframe_cmd = subparsers.add_parser(
            'plot-dataframe',
            help='Plot candles with indicators.',
            parents=[_common_parser, _strategy_parser],
        )
        plot_dataframe_cmd.set_defaults(func=start_plot_dataframe)
        self._build_args(optionlist=ARGS_PLOT_DATAFRAME, parser=plot_dataframe_cmd)

        # Plot profit
        plot_profit_cmd = subparsers.add_parser(
            'plot-profit',
            help='Generate plot showing profits.',
            parents=[_common_parser],
        )
        plot_profit_cmd.set_defaults(func=start_plot_profit)
        self._build_args(optionlist=ARGS_PLOT_PROFIT, parser=plot_profit_cmd)

        # Add hyperopt-list subcommand
        hyperopt_list_cmd = subparsers.add_parser(
            'hyperopt-list',
            help='List Hyperopt results',
            parents=[_common_parser],
        )
        hyperopt_list_cmd.set_defaults(func=start_hyperopt_list)
        self._build_args(optionlist=ARGS_HYPEROPT_LIST, parser=hyperopt_list_cmd)

        # Add hyperopt-show subcommand
        hyperopt_show_cmd = subparsers.add_parser(
            'hyperopt-show',
            help='Show details of Hyperopt results',
            parents=[_common_parser],
        )
        hyperopt_show_cmd.set_defaults(func=start_hyperopt_show)
        self._build_args(optionlist=ARGS_HYPEROPT_SHOW, parser=hyperopt_show_cmd)