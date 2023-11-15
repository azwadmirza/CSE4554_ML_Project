    def process_key_logfile(self):
        if self.options.key_logfile:
            # XXX: Remove '--key-logfile' support in 0.18.0
            # In < 0.18.0 error out
            utils.warn_until(
                'Hydrogen',
                'Remove \'--key-logfile\' support',
                _dont_call_warnings=True
            )
            self.error(
                'The \'--key-logfile\' option has been deprecated in favour '
                'of \'--log-file\''
            )