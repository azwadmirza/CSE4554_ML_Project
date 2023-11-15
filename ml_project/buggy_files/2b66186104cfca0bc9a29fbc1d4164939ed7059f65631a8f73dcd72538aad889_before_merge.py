    def __init__(self, scfg=None, ignore_singleton=False, autoload_discovery=True):
        """
        A Session object is created which is configured following a copy of the
        SessionStartupConfig scfg. (copy constructor used internally)

        @param scfg SessionStartupConfig object or None, in which case we
        look for a saved session in the default location (state dir). If
        we can't find it, we create a new SessionStartupConfig() object to
        serve as startup config. Next, the config is saved in the directory
        indicated by its 'state_dir' attribute.

        In the current implementation only a single session instance can exist
        at a time in a process. The ignore_singleton flag is used for testing.
        """
        addObserver(self.unhandled_error_observer)

        if not ignore_singleton:
            if Session.__single:
                raise RuntimeError("Session is singleton")
            Session.__single = self

        self._logger = logging.getLogger(self.__class__.__name__)

        self.ignore_singleton = ignore_singleton
        self.sesslock = NoDispersyRLock()

        # Determine startup config to use
        if scfg is None:  # If no override
            scfg = SessionStartupConfig.load()
        else:  # overrides any saved config
            # Work from copy
            scfg = SessionStartupConfig(copy.copy(scfg.sessconfig))

        def create_dir(fullpath):
            if not os.path.isdir(fullpath):
                os.makedirs(fullpath)

        def set_and_create_dir(dirname, setter, default_dir):
            if dirname is None:
                setter(default_dir)
            create_dir(dirname or default_dir)

        state_dir = scfg.get_state_dir()
        set_and_create_dir(state_dir, scfg.set_state_dir, state_dir)

        set_and_create_dir(scfg.get_torrent_store_dir(),
                           scfg.set_torrent_store_dir,
                           os.path.join(scfg.get_state_dir(), STATEDIR_TORRENT_STORE_DIR))

        # metadata store
        set_and_create_dir(scfg.get_metadata_store_dir(),
                           scfg.set_metadata_store_dir,
                           os.path.join(scfg.get_state_dir(), STATEDIR_METADATA_STORE_DIR))

        set_and_create_dir(scfg.get_peer_icon_path(), scfg.set_peer_icon_path,
                           os.path.join(scfg.get_state_dir(), STATEDIR_PEERICON_DIR))

        create_dir(os.path.join(scfg.get_state_dir(), u"sqlite"))

        create_dir(os.path.join(scfg.get_state_dir(), STATEDIR_DLPSTATE_DIR))

        # Reset the nickname to something not related to the host name, it was
        # really silly to have this default on the first place.
        # TODO: Maybe move this to the upgrader?
        if socket.gethostname().decode('utf-8', 'replace') in scfg.get_nickname():
            scfg.set_nickname("Tribler user")

        if GOTM2CRYPTO:
            permidmod.init()
            # Set params that depend on state_dir
            #
            # 1. keypair
            #
            pairfilename = scfg.get_permid_keypair_filename()

            if os.path.exists(pairfilename):
                self.keypair = permidmod.read_keypair(pairfilename)
            else:
                self.keypair = permidmod.generate_keypair()

                # Save keypair
                pubfilename = os.path.join(scfg.get_state_dir(), 'ecpub.pem')
                permidmod.save_keypair(self.keypair, pairfilename)
                permidmod.save_pub_key(self.keypair, pubfilename)

            multichain_pairfilename = scfg.get_multichain_permid_keypair_filename()

            if os.path.exists(multichain_pairfilename):
                self.multichain_keypair = permidmod.read_keypair_multichain(multichain_pairfilename)
            else:
                self.multichain_keypair = permidmod.generate_keypair_multichain()

                # Save keypair
                multichain_pubfilename = os.path.join(scfg.get_state_dir(), 'ecpub_multichain.pem')
                permidmod.save_keypair_multichain(self.multichain_keypair, multichain_pairfilename)
                permidmod.save_pub_key_multichain(self.multichain_keypair, multichain_pubfilename)

        if not scfg.get_megacache():
            scfg.set_torrent_checking(0)

        self.sessconfig = scfg.sessconfig
        self.sessconfig.lock = self.sesslock

        self.selected_ports = scfg.selected_ports

        # Claim all random ports
        self.get_listen_port()
        self.get_dispersy_port()
        self.get_mainline_dht_listen_port()
        self.get_videoserver_port()

        self.get_anon_listen_port()
        self.get_tunnel_community_socks5_listen_ports()

        # Create handler for calling back the user via separate threads
        self.lm = TriblerLaunchMany()
        self.notifier = Notifier(use_pool=True)

        # Checkpoint startup config
        self.save_pstate_sessconfig()

        self.sqlite_db = None
        self.dispersy_member = None

        self.autoload_discovery = autoload_discovery

        self.tribler_config = TriblerConfig(self)
        self.setup_tribler_gui_config()