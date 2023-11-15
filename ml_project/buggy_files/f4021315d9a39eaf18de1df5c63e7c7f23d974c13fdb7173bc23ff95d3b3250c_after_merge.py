    def __init__(self, config=None, autoload_discovery=True):
        """
        A Session object is created which is configured with the Tribler configuration object.

        Only a single session instance can exist at a time in a process.

        :param config: a TriblerConfig object or None, in which case we
        look for a saved session in the default location (state dir). If
        we can't find it, we create a new TriblerConfig() object to
        serve as startup config. Next, the config is saved in the directory
        indicated by its 'state_dir' attribute.
        :param autoload_discovery: only false in the Tunnel community tests
        """
        addObserver(self.unhandled_error_observer)

        patch_crypto_be_discovery()

        self._logger = logging.getLogger(self.__class__.__name__)

        self.session_lock = RLock()

        self.config = config or TriblerConfig()
        self._logger.info("Session is using state directory: %s", self.config.get_state_dir())

        self.get_ports_in_config()
        self.create_state_directory_structure()

        self.selected_ports = self.config.selected_ports

        self.lm = TriblerLaunchMany()
        self.notifier = Notifier()

        self.upgrader_enabled = True
        self.upgrader = None
        self.readable_status = ''  # Human-readable string to indicate the status during startup/shutdown of Tribler

        self.autoload_discovery = autoload_discovery
        self.trustchain_keypair = None