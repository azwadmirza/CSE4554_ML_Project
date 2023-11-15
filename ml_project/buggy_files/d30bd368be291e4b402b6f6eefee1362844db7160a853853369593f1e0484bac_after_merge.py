    def firsttime(self):
        """ sets it as already done"""
        self.config.set('DEFAULT', 'firsttime', 'no')
        if self.cli_config.getboolean('core', 'collect_telemetry', fallback=False):
            print(PRIVACY_STATEMENT)
        else:
            self.cli_config.set_value('core', 'collect_telemetry', ask_user_for_telemetry())

        self.update()