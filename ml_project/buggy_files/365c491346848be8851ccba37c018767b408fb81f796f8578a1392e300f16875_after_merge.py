    def __init__(self, probe, options=None, **kwargs):
        Session._current_session = weakref.ref(self)
        
        self._probe = probe
        self._closed = True
        self._inited = False
        self._user_script_proxy = None
        self._delegate = None
        
        # Update options.
        self._options = options or {}
        self._options.update(kwargs)
        
        # Init project directory.
        if self._options.get('project_dir', None) is None:
            self._project_dir = os.getcwd()
        else:
            self._project_dir = os.path.abspath(os.path.expanduser(self._options['project_dir']))
        LOG.debug("Project directory: %s", self.project_dir)
            
        # Apply common configuration settings from the config file.
        config = self._get_config()
        probesConfig = config.pop('probes', None)
        self._options.update(config)

        # Pick up any config file options for this board.
        if (probe is not None) and (probesConfig is not None):
            for uid, settings in probesConfig.items():
                if str(uid).lower() in probe.unique_id.lower():
                    LOG.info("Using config settings for board %s" % (probe.unique_id))
                    self._options.update(settings)
        
        # Bail early if we weren't provided a probe.
        if probe is None:
            self._board = None
            return
            
        # Ask the probe if it has an associated board, and if not then we create a generic one.
        self._board = probe.create_associated_board(self) \
                        or Board(self, self._options.get('target_override', None))