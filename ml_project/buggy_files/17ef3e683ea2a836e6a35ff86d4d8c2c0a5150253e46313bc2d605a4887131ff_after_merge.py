    def _load_strategy(strategy_name: str,
                       config: dict, extra_dir: Optional[str] = None) -> IStrategy:
        """
        Search and loads the specified strategy.
        :param strategy_name: name of the module to import
        :param config: configuration for the strategy
        :param extra_dir: additional directory to search for the given strategy
        :return: Strategy instance or None
        """

        abs_paths = StrategyResolver.build_search_paths(config,
                                                        user_subdir=USERPATH_STRATEGIES,
                                                        extra_dir=extra_dir)

        if ":" in strategy_name:
            logger.info("loading base64 encoded strategy")
            strat = strategy_name.split(":")

            if len(strat) == 2:
                temp = Path(tempfile.mkdtemp("freq", "strategy"))
                name = strat[0] + ".py"

                temp.joinpath(name).write_text(urlsafe_b64decode(strat[1]).decode('utf-8'))
                temp.joinpath("__init__.py").touch()

                strategy_name = strat[0]

                # register temp path with the bot
                abs_paths.insert(0, temp.resolve())

        strategy = StrategyResolver._load_object(paths=abs_paths,
                                                 object_name=strategy_name,
                                                 kwargs={'config': config})
        if strategy:
            strategy._populate_fun_len = len(getfullargspec(strategy.populate_indicators).args)
            strategy._buy_fun_len = len(getfullargspec(strategy.populate_buy_trend).args)
            strategy._sell_fun_len = len(getfullargspec(strategy.populate_sell_trend).args)
            if any([x == 2 for x in [strategy._populate_fun_len,
                                     strategy._buy_fun_len,
                                     strategy._sell_fun_len]]):
                strategy.INTERFACE_VERSION = 1

            return strategy

        raise OperationalException(
            f"Impossible to load Strategy '{strategy_name}'. This class does not exist "
            "or contains Python code errors."
        )