    def register(self, session, session_lock):
        assert isInIOThread()
        if not self.registered:
            self.registered = True

            self.session = session
            self.session_lock = session_lock

            # On Mac, we bundle the root certificate for the SSL validation since Twisted is not using the root
            # certificates provided by the system trust store.
            if sys.platform == 'darwin':
                os.environ['SSL_CERT_FILE'] = os.path.join(get_lib_path(), 'root_certs_mac.pem')

            if self.session.config.get_torrent_store_enabled():
                from Tribler.Core.leveldbstore import LevelDbStore
                self.torrent_store = LevelDbStore(self.session.config.get_torrent_store_dir())

            if self.session.config.get_metadata_enabled():
                from Tribler.Core.leveldbstore import LevelDbStore
                self.metadata_store = LevelDbStore(self.session.config.get_metadata_store_dir())

            # torrent collecting: RemoteTorrentHandler
            if self.session.config.get_torrent_collecting_enabled():
                from Tribler.Core.RemoteTorrentHandler import RemoteTorrentHandler
                self.rtorrent_handler = RemoteTorrentHandler(self.session)

            # TODO(emilon): move this to a megacache component or smth
            if self.session.config.get_megacache_enabled():
                from Tribler.Core.CacheDB.SqliteCacheDBHandler import (PeerDBHandler, TorrentDBHandler,
                                                                       MyPreferenceDBHandler, VoteCastDBHandler,
                                                                       ChannelCastDBHandler)
                from Tribler.Core.Category.Category import Category

                self._logger.debug('tlm: Reading Session state from %s', self.session.config.get_state_dir())

                self.category = Category()

                # create DBHandlers
                self.peer_db = PeerDBHandler(self.session)
                self.torrent_db = TorrentDBHandler(self.session)
                self.mypref_db = MyPreferenceDBHandler(self.session)
                self.votecast_db = VoteCastDBHandler(self.session)
                self.channelcast_db = ChannelCastDBHandler(self.session)

                # initializes DBHandlers
                self.peer_db.initialize()
                self.torrent_db.initialize()
                self.mypref_db.initialize()
                self.votecast_db.initialize()
                self.channelcast_db.initialize()

                from Tribler.Core.Modules.tracker_manager import TrackerManager
                self.tracker_manager = TrackerManager(self.session)
                self.tracker_manager.initialize()

            if self.session.config.get_video_server_enabled():
                self.video_server = VideoServer(self.session.config.get_video_server_port(), self.session)
                self.video_server.start()

            # Dispersy
            self.tftp_handler = None
            if self.session.config.get_dispersy_enabled():
                from Tribler.dispersy.dispersy import Dispersy
                from Tribler.dispersy.endpoint import StandaloneEndpoint

                # set communication endpoint
                endpoint = StandaloneEndpoint(self.session.config.get_dispersy_port())

                working_directory = unicode(self.session.config.get_state_dir())
                self.dispersy = Dispersy(endpoint, working_directory)

                # register TFTP service
                from Tribler.Core.TFTP.handler import TftpHandler
                self.tftp_handler = TftpHandler(self.session, endpoint, "fffffffd".decode('hex'), block_size=1024)
                self.tftp_handler.initialize()

            if self.session.config.get_torrent_search_enabled() or self.session.config.get_channel_search_enabled():
                self.search_manager = SearchManager(self.session)
                self.search_manager.initialize()

        if not self.initComplete:
            self.init()

        self.session.add_observer(self.on_tribler_started, NTFY_TRIBLER, [NTFY_STARTED])
        self.session.notifier.notify(NTFY_TRIBLER, NTFY_STARTED, None)
        return self.startup_deferred