    def _load_config(self, filename=None, config=None, replace=True):
        if self.config_session is None:
            self.config_session = "napalm_{}".format(datetime.now().microsecond)

        commands = []
        commands.append("configure session {}".format(self.config_session))
        if replace:
            commands.append("rollback clean-config")

        if filename is not None:
            with open(filename, "r") as f:
                lines = f.readlines()
        else:
            if isinstance(config, list):
                lines = config
            else:
                lines = config.splitlines()

        for line in lines:
            line = line.strip()
            if line == "":
                continue
            if line.startswith("!") and not line.startswith("!!"):
                continue
            commands.append(line)

        for start, depth in [
            (s, d) for (s, d) in self.HEREDOC_COMMANDS if s in commands
        ]:
            commands = self._multiline_convert(commands, start=start, depth=depth)

        commands = self._mode_comment_convert(commands)

        try:
            if self.eos_autoComplete is not None:
                self.device.run_commands(commands, autoComplete=self.eos_autoComplete)
            else:
                self.device.run_commands(commands)
        except pyeapi.eapilib.CommandError as e:
            self.discard_config()
            msg = str(e)
            if replace:
                raise ReplaceConfigException(msg)
            else:
                raise MergeConfigException(msg)