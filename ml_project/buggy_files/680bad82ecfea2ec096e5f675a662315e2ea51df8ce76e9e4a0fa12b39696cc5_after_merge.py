    def init(self):
        # Wallets
        if self.session.config.get_bitcoinlib_enabled():
            try:
                from anydex.wallet.btc_wallet import BitcoinWallet, BitcoinTestnetWallet
                wallet_path = os.path.join(self.session.config.get_state_dir(), 'wallet')
                btc_wallet = BitcoinWallet(wallet_path)
                btc_testnet_wallet = BitcoinTestnetWallet(wallet_path)
                self.wallets[btc_wallet.get_identifier()] = btc_wallet
                self.wallets[btc_testnet_wallet.get_identifier()] = btc_testnet_wallet
            except Exception as exc:
                self._logger.error("bitcoinlib library cannot be loaded: %s", exc)

        if self.session.config.get_chant_enabled():
            channels_dir = os.path.join(self.session.config.get_chant_channels_dir())
            metadata_db_name = 'metadata.db' if not self.session.config.get_testnet() else 'metadata_testnet.db'
            database_path = os.path.join(self.session.config.get_state_dir(), 'sqlite', metadata_db_name)
            self.mds = MetadataStore(database_path, channels_dir, self.session.trustchain_keypair)

        if self.session.config.get_dummy_wallets_enabled():
            # For debugging purposes, we create dummy wallets
            dummy_wallet1 = DummyWallet1()
            self.wallets[dummy_wallet1.get_identifier()] = dummy_wallet1

            dummy_wallet2 = DummyWallet2()
            self.wallets[dummy_wallet2.get_identifier()] = dummy_wallet2

        if self.session.config.get_torrent_checking_enabled():
            self.session.readable_status = STATE_START_TORRENT_CHECKER
            self.torrent_checker = TorrentChecker(self.session)
            self.torrent_checker.initialize()

        if self.ipv8:
            self.ipv8_start_time = time.time()
            self.load_ipv8_overlays()
            self.enable_ipv8_statistics()

        tunnel_community_ports = self.session.config.get_tunnel_community_socks5_listen_ports()
        self.session.config.set_anon_proxy_settings(2, ("127.0.0.1", tunnel_community_ports))

        if self.session.config.get_libtorrent_enabled():
            self.session.readable_status = STATE_START_LIBTORRENT
            from Tribler.Core.Libtorrent.LibtorrentMgr import LibtorrentMgr
            self.ltmgr = LibtorrentMgr(self.session)
            self.ltmgr.initialize()
            for port, protocol in self.upnp_ports:
                self.ltmgr.add_upnp_mapping(port, protocol)

        if self.session.config.get_chant_enabled():
            self.gigachannel_manager = GigaChannelManager(self.session)
            # GigaChannel Manager startup routines are started asynchronously by Session
            # after resuming Libtorrent downloads.

        if self.api_manager:
            self.session.readable_status = STATE_START_API_ENDPOINTS
            self.api_manager.root_endpoint.start_endpoints()

        if self.session.config.get_watch_folder_enabled():
            self.session.readable_status = STATE_START_WATCH_FOLDER
            self.watch_folder = WatchFolder(self.session)
            self.watch_folder.start()

        if self.session.config.get_credit_mining_enabled():
            self.session.readable_status = STATE_START_CREDIT_MINING
            from Tribler.Core.CreditMining.CreditMiningManager import CreditMiningManager
            self.credit_mining_manager = CreditMiningManager(self.session)

        if self.session.config.get_resource_monitor_enabled():
            self.resource_monitor = ResourceMonitor(self.session)
            self.resource_monitor.start()

        if self.session.config.get_version_checker_enabled():
            self.version_check_manager = VersionCheckManager(self.session)
            self.version_check_manager.start()

        self.session.set_download_states_callback(self.sesscb_states_callback)

        if self.session.config.get_ipv8_enabled() and self.session.config.get_trustchain_enabled():
            self.payout_manager = PayoutManager(self.trustchain_community, self.dht_community)

        self.initComplete = True