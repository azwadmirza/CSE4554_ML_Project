    def _process_plot_options(self, config: Dict[str, Any]) -> None:

        self._args_to_config(config, argname='pairs',
                             logstring='Using pairs {}')

        self._args_to_config(config, argname='indicators1',
                             logstring='Using indicators1: {}')

        self._args_to_config(config, argname='indicators2',
                             logstring='Using indicators2: {}')

        self._args_to_config(config, argname='plot_limit',
                             logstring='Limiting plot to: {}')
        self._args_to_config(config, argname='trade_source',
                             logstring='Using trades from: {}')

        self._args_to_config(config, argname='erase',
                             logstring='Erase detected. Deleting existing data.')

        self._args_to_config(config, argname='timeframes',
                             logstring='timeframes --timeframes: {}')

        self._args_to_config(config, argname='days',
                             logstring='Detected --days: {}')

        self._args_to_config(config, argname='download_trades',
                             logstring='Detected --dl-trades: {}')

        self._args_to_config(config, argname='dataformat_ohlcv',
                             logstring='Using "{}" to store OHLCV data.')

        self._args_to_config(config, argname='dataformat_trades',
                             logstring='Using "{}" to store trades data.')