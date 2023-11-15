    def __init__(self, state_dir, config_file=None):
        """
        Create a new TriblerConfig instance.

        :param config_file: path to existing config file
        :raises an InvalidConfigException if ConfigObj is invalid
        """
        self._logger = logging.getLogger(self.__class__.__name__)
        self._state_dir = Path(state_dir)
        self.config = ConfigObj(infile=(str(config_file) if config_file else None),
                                configspec=str(CONFIG_SPEC_PATH), default_encoding='utf-8')
        self.validate()
        self.selected_ports = {}