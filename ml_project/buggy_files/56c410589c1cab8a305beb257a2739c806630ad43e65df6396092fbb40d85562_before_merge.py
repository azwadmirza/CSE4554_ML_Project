    def make_handler(self, app):
        return app.make_handler(
            logger=self.log,
            debug=self.cfg.debug,
            timeout=self.cfg.timeout,
            keep_alive=self.cfg.keepalive,
            access_log=self.log.access_log,
            access_log_format=self._get_valid_log_format(
                self.cfg.access_log_format))