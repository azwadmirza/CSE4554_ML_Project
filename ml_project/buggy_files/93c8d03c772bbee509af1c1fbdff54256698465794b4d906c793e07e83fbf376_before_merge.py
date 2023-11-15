    def early_shutdown(self):
        """ Called as soon as Session shutdown is initiated. Used to start
        shutdown tasks that takes some time and that can run in parallel
        to checkpointing, etc.
        :returns a Deferred that will fire once all dependencies acknowledge they have shutdown.
        """
        self._logger.info("tlm: early_shutdown")

        self.shutdown_task_manager()

        # Note: session_lock not held
        self.shutdownstarttime = timemod.time()
        if self.credit_mining_manager:
            yield self.credit_mining_manager.shutdown()
        self.credit_mining_manager = None

        if self.torrent_checker:
            yield self.torrent_checker.shutdown()
        self.torrent_checker = None

        if self.channel_manager:
            yield self.channel_manager.shutdown()
        self.channel_manager = None

        if self.search_manager:
            yield self.search_manager.shutdown()
        self.search_manager = None

        if self.rtorrent_handler:
            yield self.rtorrent_handler.shutdown()
        self.rtorrent_handler = None

        if self.video_server:
            yield self.video_server.shutdown_server()
        self.video_server = None

        if self.version_check_manager:
            self.version_check_manager.stop()
        self.version_check_manager = None

        if self.resource_monitor:
            self.resource_monitor.stop()
        self.resource_monitor = None

        self.tracker_manager = None

        if self.tunnel_community and self.trustchain_community:
            # We unload these overlays manually since the TrustChain has to be unloaded after the tunnel overlay.
            yield self.ipv8.unload_overlay(self.tunnel_community)
            yield self.ipv8.unload_overlay(self.trustchain_community)

        if self.dispersy:
            self._logger.info("lmc: Shutting down Dispersy...")
            now = timemod.time()
            try:
                success = yield self.dispersy.stop()
            except:
                print_exc()
                success = False

            diff = timemod.time() - now
            if success:
                self._logger.info("lmc: Dispersy successfully shutdown in %.2f seconds", diff)
            else:
                self._logger.info("lmc: Dispersy failed to shutdown in %.2f seconds", diff)

        if self.ipv8:
            yield self.ipv8.stop(stop_reactor=False)

        if self.metadata_store is not None:
            yield self.metadata_store.close()
        self.metadata_store = None

        if self.tftp_handler is not None:
            yield self.tftp_handler.shutdown()
        self.tftp_handler = None

        if self.channelcast_db is not None:
            yield self.channelcast_db.close()
        self.channelcast_db = None

        if self.votecast_db is not None:
            yield self.votecast_db.close()
        self.votecast_db = None

        if self.mypref_db is not None:
            yield self.mypref_db.close()
        self.mypref_db = None

        if self.torrent_db is not None:
            yield self.torrent_db.close()
        self.torrent_db = None

        if self.peer_db is not None:
            yield self.peer_db.close()
        self.peer_db = None

        if self.mainline_dht is not None:
            from Tribler.Core.DecentralizedTracking import mainlineDHT
            yield mainlineDHT.deinit(self.mainline_dht)
        self.mainline_dht = None

        if self.torrent_store is not None:
            yield self.torrent_store.close()
        self.torrent_store = None

        if self.watch_folder is not None:
            yield self.watch_folder.stop()
        self.watch_folder = None

        # We close the API manager as late as possible during shutdown.
        if self.api_manager is not None:
            yield self.api_manager.stop()
        self.api_manager = None