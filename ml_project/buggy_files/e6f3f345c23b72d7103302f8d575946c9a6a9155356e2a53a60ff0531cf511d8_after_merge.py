    def process_log_level(self):
        if not self.options.log_level:
            cli_log_level = 'cli_{0}_log_level'.format(
                self.get_prog_name().replace('-', '_')
            )
            if self.config.get(cli_log_level, None) is not None:
                self.options.log_level = self.config.get(cli_log_level)
            elif self.config.get(self._loglevel_config_setting_name_, None):
                self.options.log_level = self.config.get(
                    self._loglevel_config_setting_name_
                )
            else:
                self.options.log_level = self._default_logging_level_

        # Setup extended logging right before the last step
        self._mixin_after_parsed_funcs.append(self.__setup_extended_logging)
        # Setup the multiprocessing log queue listener if enabled
        self._mixin_after_parsed_funcs.append(self._setup_mp_logging_listener)
        # Setup the console as the last _mixin_after_parsed_func to run
        self._mixin_after_parsed_funcs.append(self.__setup_console_logger)