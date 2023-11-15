    def register(self, session, session_lock):
        assert isInIOThread()

        self.session = session
        self.session_lock = session_lock

        self.tracker_manager = TrackerManager(self.session)

        # On Mac, we bundle the root certificate for the SSL validation since Twisted is not using the root
        # certificates provided by the system trust store.
        if sys.platform == 'darwin':
            os.environ['SSL_CERT_FILE'] = os.path.join(get_lib_path(), 'root_certs_mac.pem')

        if self.session.config.get_video_server_enabled():
            self.video_server = VideoServer(self.session.config.get_video_server_port(), self.session)
            self.video_server.start()

        # IPv8
        if self.session.config.get_ipv8_enabled():
            from ipv8.configuration import get_default_configuration
            ipv8_config = get_default_configuration()
            ipv8_config['port'] = self.session.config.get_ipv8_port()
            ipv8_config['address'] = self.session.config.get_ipv8_address()
            ipv8_config['overlays'] = []
            ipv8_config['keys'] = []  # We load the keys ourselves

            if self.session.config.get_ipv8_bootstrap_override():
                import ipv8.community as community_file
                community_file._DEFAULT_ADDRESSES = [self.session.config.get_ipv8_bootstrap_override()]
                community_file._DNS_ADDRESSES = []

            self.ipv8 = IPv8(ipv8_config, enable_statistics=self.session.config.get_ipv8_statistics())

            self.session.config.set_anon_proxy_settings(2, ("127.0.0.1",
                                                            self.session.
                                                            config.get_tunnel_community_socks5_listen_ports()))
        self.init()