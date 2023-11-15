    def load_strategy(config: Optional[Dict] = None) -> IStrategy:
        """
        Load the custom class from config parameter
        :param config: configuration dictionary or None
        """
        config = config or {}

        if not config.get('strategy'):
            raise OperationalException("No strategy set. Please use `--strategy` to specify "
                                       "the strategy class to use.")

        strategy_name = config['strategy']
        strategy: IStrategy = StrategyResolver._load_strategy(
            strategy_name, config=config,
            extra_dir=config.get('strategy_path'))

        # make sure ask_strategy dict is available
        if 'ask_strategy' not in config:
            config['ask_strategy'] = {}

        # Set attributes
        # Check if we need to override configuration
        #             (Attribute name,                    default,     ask_strategy)
        attributes = [("minimal_roi",                     {"0": 10.0}, False),
                      ("ticker_interval",                 None,        False),
                      ("stoploss",                        None,        False),
                      ("trailing_stop",                   None,        False),
                      ("trailing_stop_positive",          None,        False),
                      ("trailing_stop_positive_offset",   0.0,         False),
                      ("trailing_only_offset_is_reached", None,        False),
                      ("process_only_new_candles",        None,        False),
                      ("order_types",                     None,        False),
                      ("order_time_in_force",             None,        False),
                      ("stake_currency",                  None,        False),
                      ("stake_amount",                    None,        False),
                      ("startup_candle_count",            None,        False),
                      ("unfilledtimeout",                 None,        False),
                      ("use_sell_signal",                 True,        True),
                      ("sell_profit_only",                False,       True),
                      ("ignore_roi_if_buy_signal",        False,       True),
                      ]
        for attribute, default, ask_strategy in attributes:
            if ask_strategy:
                StrategyResolver._override_attribute_helper(strategy, config['ask_strategy'],
                                                            attribute, default)
            else:
                StrategyResolver._override_attribute_helper(strategy, config,
                                                            attribute, default)

        # Loop this list again to have output combined
        for attribute, _, exp in attributes:
            if exp and attribute in config['ask_strategy']:
                logger.info("Strategy using %s: %s", attribute, config['ask_strategy'][attribute])
            elif attribute in config:
                logger.info("Strategy using %s: %s", attribute, config[attribute])

        # Sort and apply type conversions
        strategy.minimal_roi = OrderedDict(sorted(
            {int(key): value for (key, value) in strategy.minimal_roi.items()}.items(),
            key=lambda t: t[0]))
        strategy.stoploss = float(strategy.stoploss)

        StrategyResolver._strategy_sanity_validations(strategy)
        return strategy