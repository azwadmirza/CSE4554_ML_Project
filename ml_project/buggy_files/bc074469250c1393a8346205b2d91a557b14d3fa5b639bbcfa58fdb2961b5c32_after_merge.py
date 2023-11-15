    def _load_config(self) -> None:
        """Load config, monitors, alerters and loggers."""

        config = EnvironmentAwareConfigParser()
        if not self._config_file.exists():
            raise RuntimeError(
                "Configuration file {} does not exist".format(self._config_file)
            )
        config.read(self._config_file)

        self.interval = config.getint("monitor", "interval")
        self.pidfile = config.get("monitor", "pidfile", fallback=None)
        hup_file = config.get("monitor", "hup_file", fallback=None)
        if hup_file is not None:
            self._hup_file = Path(hup_file)
            module_logger.info(
                "Watching modification time of %s; increase it to trigger a config reload",
                hup_file,
            )
            self._check_hup_file()

        if (
            not self._no_network
            and config.get("monitor", "remote", fallback="0") == "1"
        ):
            self._network = True
            self._remote_port = int(config.get("monitor", "remote_port"))
            self._network_key = config.get("monitor", "key", fallback=None)
            self._network_bind_host = config.get("monitor", "bind_host", fallback="")
            self._ipv4_only = cast(
                bool, config.get("monitor", "ipv4_only", fallback=False)
            )
        else:
            self._network = False

        monitors_file = Path(config.get("monitor", "monitors", fallback="monitors.ini"))
        self._load_monitors(monitors_file)
        count = self.count_monitors()
        if count == 0:
            module_logger.critical("No monitors loaded :(")
        self._load_loggers(config)
        self._load_alerters(config)
        if not self._verify_dependencies():
            raise RuntimeError("Broken dependency configuration")
        if not self.verify_alerting():
            module_logger.critical("No alerters defined and no remote logger found")