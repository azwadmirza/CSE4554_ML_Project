    def start(self):
        """
        Start a Tribler session by initializing the LaunchManyCore class, opening the database and running the upgrader.
        Returns a deferred that fires when the Tribler session is ready for use.
        """
        # Start the REST API before the upgrader since we want to send interesting upgrader events over the socket
        if self.config.get_http_api_enabled():
            self.lm.api_manager = RESTManager(self)
            self.readable_status = STATE_START_API
            self.lm.api_manager.start()

        if self.upgrader_enabled:
            self.upgrader = TriblerUpgrader(self)
            self.readable_status = STATE_UPGRADING_READABLE
            upgrader_deferred = self.upgrader.run()
        else:
            upgrader_deferred = succeed(None)

        def after_upgrade(_):
            self.upgrader = None

        def log_upgrader_error(failure):
            self._logger.error("Error in Upgrader callback chain: %s", failure)

        def on_tribler_started(_):
            self.notifier.notify(NTFY_TRIBLER, NTFY_STARTED, None)

        startup_deferred = upgrader_deferred. \
            addCallbacks(lambda _: self.lm.register(self, self.session_lock), log_upgrader_error). \
            addCallbacks(after_upgrade, log_upgrader_error). \
            addCallback(on_tribler_started)

        def load_checkpoint(_):
            if self.config.get_libtorrent_enabled():
                self.readable_status = STATE_LOAD_CHECKPOINTS
                self.load_checkpoint()
            self.readable_status = STATE_READABLE_STARTED

        def start_gigachannel_manager(_):
            # GigaChannel Manager should be started *after* resuming the downloads,
            # because it depends on the states of torrent downloads
            # TODO: move GigaChannel torrents into a separate session
            if self.lm.gigachannel_manager:
                self.lm.gigachannel_manager.start()

        def start_bootstrap_download(_):
            if not self.lm.bootstrap:
                self.lm.start_bootstrap_download()

        return startup_deferred.addCallback(load_checkpoint).addCallback(start_gigachannel_manager)\
            .addCallback(start_bootstrap_download)