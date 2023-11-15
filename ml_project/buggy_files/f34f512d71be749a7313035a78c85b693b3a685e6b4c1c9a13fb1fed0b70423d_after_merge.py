    def __init__(self, *args, **kwargs):
        self.tribler_session = kwargs.pop('tribler_session', None)
        num_competing_slots = kwargs.pop('competing_slots', 15)
        num_random_slots = kwargs.pop('random_slots', 5)
        self.bandwidth_wallet = kwargs.pop('bandwidth_wallet', None)
        socks_listen_ports = kwargs.pop('socks_listen_ports', None)
        state_path = self.tribler_session.config.get_state_dir() if self.tribler_session else path_util.Path()
        self.exitnode_cache = kwargs.pop('exitnode_cache', state_path / 'exitnode_cache.dat')
        super(TriblerTunnelCommunity, self).__init__(*args, **kwargs)
        self._use_main_thread = True

        if self.tribler_session:
            if self.tribler_session.config.get_tunnel_community_exitnode_enabled():
                self.settings.peer_flags.add(PEER_FLAG_EXIT_BT)
                self.settings.peer_flags.add(PEER_FLAG_EXIT_IPV8)

            if not socks_listen_ports:
                socks_listen_ports = self.tribler_session.config.get_tunnel_community_socks5_listen_ports()
        elif socks_listen_ports is None:
            socks_listen_ports = range(1080, 1085)

        self.bittorrent_peers = {}
        self.dispatcher = TunnelDispatcher(self)
        self.download_states = {}
        self.competing_slots = [(0, None)] * num_competing_slots  # 1st tuple item = token balance, 2nd = circuit id
        self.random_slots = [None] * num_random_slots
        self.reject_callback = None  # This callback is invoked with a tuple (time, balance) when we reject a circuit
        self.last_forced_announce = {}

        # Start the SOCKS5 servers
        self.socks_servers = []
        for port in socks_listen_ports:
            socks_server = Socks5Server(port, self.dispatcher)
            self.register_task('start_socks_%d' % port, socks_server.start)
            self.socks_servers.append(socks_server)

        self.dispatcher.set_socks_servers(self.socks_servers)

        self.add_message_handler(PayoutPayload, self.on_payout_block)

        self.add_cell_handler(BalanceRequestPayload, self.on_balance_request_cell)
        self.add_cell_handler(RelayBalanceRequestPayload, self.on_relay_balance_request_cell)
        self.add_cell_handler(BalanceResponsePayload, self.on_balance_response_cell)
        self.add_cell_handler(RelayBalanceResponsePayload, self.on_relay_balance_response_cell)

        NO_CRYPTO_PACKETS.extend([24, 26])

        if self.exitnode_cache:
            self.restore_exitnodes_from_disk()