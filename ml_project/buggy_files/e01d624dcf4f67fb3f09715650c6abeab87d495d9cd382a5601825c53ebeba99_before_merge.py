    def _process_optimize_options(self, config: Dict[str, Any]) -> None:

        # This will override the strategy configuration
        self._args_to_config(config, argname='ticker_interval',
                             logstring='Parameter -i/--ticker-interval detected ... '
                             'Using ticker_interval: {} ...')

        self._args_to_config(config, argname='position_stacking',
                             logstring='Parameter --enable-position-stacking detected ...')

        # Setting max_open_trades to infinite if -1
        if config.get('max_open_trades') == -1:
            config['max_open_trades'] = float('inf')

        if 'use_max_market_positions' in self.args and not self.args["use_max_market_positions"]:
            config.update({'use_max_market_positions': False})
            logger.info('Parameter --disable-max-market-positions detected ...')
            logger.info('max_open_trades set to unlimited ...')
        elif 'max_open_trades' in self.args and self.args["max_open_trades"]:
            config.update({'max_open_trades': self.args["max_open_trades"]})
            logger.info('Parameter --max-open-trades detected, '
                        'overriding max_open_trades to: %s ...', config.get('max_open_trades'))
        elif config['runmode'] in NON_UTIL_MODES:
            logger.info('Using max_open_trades: %s ...', config.get('max_open_trades'))

        self._args_to_config(config, argname='stake_amount',
                             logstring='Parameter --stake-amount detected, '
                             'overriding stake_amount to: {} ...')

        self._args_to_config(config, argname='fee',
                             logstring='Parameter --fee detected, '
                             'setting fee to: {} ...')

        self._args_to_config(config, argname='timerange',
                             logstring='Parameter --timerange detected: {} ...')

        self._process_datadir_options(config)

        self._args_to_config(config, argname='strategy_list',
                             logstring='Using strategy list of {} strategies', logfun=len)

        self._args_to_config(config, argname='ticker_interval',
                             logstring='Overriding ticker interval with Command line argument')

        self._args_to_config(config, argname='export',
                             logstring='Parameter --export detected: {} ...')

        # Edge section:
        if 'stoploss_range' in self.args and self.args["stoploss_range"]:
            txt_range = eval(self.args["stoploss_range"])
            config['edge'].update({'stoploss_range_min': txt_range[0]})
            config['edge'].update({'stoploss_range_max': txt_range[1]})
            config['edge'].update({'stoploss_range_step': txt_range[2]})
            logger.info('Parameter --stoplosses detected: %s ...', self.args["stoploss_range"])

        # Hyperopt section
        self._args_to_config(config, argname='hyperopt',
                             logstring='Using Hyperopt class name: {}')

        self._args_to_config(config, argname='hyperopt_path',
                             logstring='Using additional Hyperopt lookup path: {}')

        self._args_to_config(config, argname='epochs',
                             logstring='Parameter --epochs detected ... '
                             'Will run Hyperopt with for {} epochs ...'
                             )

        self._args_to_config(config, argname='spaces',
                             logstring='Parameter -s/--spaces detected: {}')

        self._args_to_config(config, argname='print_all',
                             logstring='Parameter --print-all detected ...')

        if 'print_colorized' in self.args and not self.args["print_colorized"]:
            logger.info('Parameter --no-color detected ...')
            config.update({'print_colorized': False})
        else:
            config.update({'print_colorized': True})

        self._args_to_config(config, argname='print_json',
                             logstring='Parameter --print-json detected ...')

        self._args_to_config(config, argname='hyperopt_jobs',
                             logstring='Parameter -j/--job-workers detected: {}')

        self._args_to_config(config, argname='hyperopt_random_state',
                             logstring='Parameter --random-state detected: {}')

        self._args_to_config(config, argname='hyperopt_min_trades',
                             logstring='Parameter --min-trades detected: {}')

        self._args_to_config(config, argname='hyperopt_continue',
                             logstring='Hyperopt continue: {}')

        self._args_to_config(config, argname='hyperopt_loss',
                             logstring='Using Hyperopt loss class name: {}')

        self._args_to_config(config, argname='hyperopt_show_index',
                             logstring='Parameter -n/--index detected: {}')

        self._args_to_config(config, argname='hyperopt_list_best',
                             logstring='Parameter --best detected: {}')

        self._args_to_config(config, argname='hyperopt_list_profitable',
                             logstring='Parameter --profitable detected: {}')

        self._args_to_config(config, argname='hyperopt_list_no_details',
                             logstring='Parameter --no-details detected: {}')

        self._args_to_config(config, argname='hyperopt_show_no_header',
                             logstring='Parameter --no-header detected: {}')