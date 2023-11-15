    def make_handler(self, app):
        if hasattr(self.cfg, 'debug'):
            is_debug = self.cfg.debug
        else:
            is_debug = self.log.loglevel == logging.DEBUG

        return app.make_handler(
            logger=self.log,
            debug=is_debug,
            slow_request_timeout=self.cfg.timeout,
            keepalive_timeout=self.cfg.keepalive,
            access_log=self.log.access_log,
            access_log_format=self._get_valid_log_format(
                self.cfg.access_log_format))