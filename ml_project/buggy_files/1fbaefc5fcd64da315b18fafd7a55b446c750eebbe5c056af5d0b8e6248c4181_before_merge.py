    def __init__(self, config=None):
        """
        Create a new TriblerConfig instance.

        :param config: a ConfigObj instance
        :raises an InvalidConfigException if ConfigObj is invalid
        """
        self._logger = logging.getLogger(self.__class__.__name__)

        if config is None:
            file_name = os.path.join(self.get_default_state_dir(), FILENAME)
            if os.path.exists(file_name):
                config = ConfigObj(file_name, configspec=CONFIG_SPEC_PATH, encoding='latin_1')
            else:
                config = ConfigObj(configspec=CONFIG_SPEC_PATH, encoding='latin_1')
        self.config = config
        self.validate()

        self.selected_ports = {}
        self._set_video_analyser_path()