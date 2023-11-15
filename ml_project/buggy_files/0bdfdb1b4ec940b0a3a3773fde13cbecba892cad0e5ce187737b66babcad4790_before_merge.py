    def start_tribler(self, options):
        """
        Main method to startup Tribler.
        """
        def on_shutdown(_):
            msg("Tribler shut down")
            self.process_checker.remove_lock_file()
            reactor.stop()

        def signal_handler(sig, _):
            msg("Received shut down signal %s" % sig)
            if not self._stopping:
                self._stopping = True
                self.session.shutdown().addCallback(on_shutdown)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        config = SessionStartupConfig().load()  # Load the default configuration file
        config.set_http_api_enabled(True)

        # Check if we are already running a Tribler instance
        self.process_checker = ProcessChecker()
        if self.process_checker.already_running:
            self.shutdown_process("Another Tribler instance is already using statedir %s" % config.get_state_dir())
            return

        msg("Starting Tribler")

        if options["statedir"]:
            config.set_state_dir(options["statedir"])

        if options["restapi"] > 0:
            config.set_http_api_enabled(True)
            config.set_http_api_port(options["restapi"])

        if options["dispersy"] != -1 and options["dispersy"] > 0:
            config.set_dispersy_port(options["dispersy"])

        if options["libtorrent"] != -1 and options["libtorrent"] > 0:
            config.set_listen_port(options["libtorrent"])

        self.session = Session(config)
        upgrader = self.session.prestart()
        if upgrader.failed:
            self.shutdown_process("The upgrader failed: .Tribler directory backed up, aborting")
        else:
            self.session.start()
            msg("Tribler started")

        if "auto-join-channel" in options and options["auto-join-channel"]:
            msg("Enabling auto-joining of channels")
            for community in self.session.get_dispersy_instance().get_communities():
                if isinstance(community, AllChannelCommunity):
                    community.auto_join_channel = True

        if "log-incoming-searches" in options and options["log-incoming-searches"]:
            msg("Logging incoming remote searches")
            for community in self.session.get_dispersy_instance().get_communities():
                if isinstance(community, SearchCommunity):
                    community.log_incoming_searches = self.log_incoming_remote_search