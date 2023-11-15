    def start_bootstrap_download(self):
        if self.session.config.get_bootstrap_enabled():
            if not self.payout_manager:
                self._logger.warn("Running bootstrap without payout enabled")
            self.bootstrap = Bootstrap(self.session.config.get_state_dir(), dht=self.dht_community)
            self.bootstrap.start_by_infohash(self.session.start_download_from_tdef,
                                             self.session.config.get_bootstrap_infohash())