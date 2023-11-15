    def do_update(self):
        self.provider.set_node_tags(
            self.node_id, {TAG_RAY_NODE_STATUS: STATUS_WAITING_FOR_SSH})
        cli_logger.labeled_value("New status", STATUS_WAITING_FOR_SSH)

        deadline = time.time() + NODE_START_WAIT_S
        self.wait_ready(deadline)

        node_tags = self.provider.node_tags(self.node_id)
        logger.debug("Node tags: {}".format(str(node_tags)))

        # runtime_hash will only change whenever the user restarts
        # or updates their cluster with `get_or_create_head_node`
        if node_tags.get(TAG_RAY_RUNTIME_CONFIG) == self.runtime_hash and (
                self.file_mounts_contents_hash is None
                or node_tags.get(TAG_RAY_FILE_MOUNTS_CONTENTS) ==
                self.file_mounts_contents_hash):
            # todo: we lie in the confirmation message since
            # full setup might be cancelled here
            cli_logger.print(
                "Configuration already up to date, "
                "skipping file mounts, initalization and setup commands.")
            cli_logger.old_info(logger,
                                "{}{} already up-to-date, skip to ray start",
                                self.log_prefix, self.node_id)

        else:
            cli_logger.print(
                "Updating cluster configuration.",
                _tags=dict(hash=self.runtime_hash))

            self.provider.set_node_tags(
                self.node_id, {TAG_RAY_NODE_STATUS: STATUS_SYNCING_FILES})
            cli_logger.labeled_value("New status", STATUS_SYNCING_FILES)
            self.sync_file_mounts(self.rsync_up)

            # Only run setup commands if runtime_hash has changed because
            # we don't want to run setup_commands every time the head node
            # file_mounts folders have changed.
            if node_tags.get(TAG_RAY_RUNTIME_CONFIG) != self.runtime_hash:
                # Run init commands
                self.provider.set_node_tags(
                    self.node_id, {TAG_RAY_NODE_STATUS: STATUS_SETTING_UP})
                cli_logger.labeled_value("New status", STATUS_SETTING_UP)

                if self.initialization_commands:
                    with cli_logger.group(
                            "Running initialization commands",
                            _numbered=("[]", 4,
                                       6)):  # todo: fix command numbering
                        with LogTimer(
                                self.log_prefix + "Initialization commands",
                                show_status=True):

                            for cmd in self.initialization_commands:
                                self.cmd_runner.run(
                                    cmd,
                                    ssh_options_override=SSHOptions(
                                        self.auth_config.get(
                                            "ssh_private_key")))
                else:
                    cli_logger.print(
                        "No initialization commands to run.",
                        _numbered=("[]", 4, 6))

                if self.setup_commands:
                    with cli_logger.group(
                            "Running setup commands",
                            _numbered=("[]", 5,
                                       6)):  # todo: fix command numbering
                        with LogTimer(
                                self.log_prefix + "Setup commands",
                                show_status=True):

                            total = len(self.setup_commands)
                            for i, cmd in enumerate(self.setup_commands):
                                if cli_logger.verbosity == 0:
                                    cmd_to_print = cf.bold(cmd[:30]) + "..."
                                else:
                                    cmd_to_print = cf.bold(cmd)

                                cli_logger.print(
                                    "{}",
                                    cmd_to_print,
                                    _numbered=("()", i, total))

                                self.cmd_runner.run(cmd)
                else:
                    cli_logger.print(
                        "No setup commands to run.", _numbered=("[]", 5, 6))

        with cli_logger.group(
                "Starting the Ray runtime", _numbered=("[]", 6, 6)):
            with LogTimer(
                    self.log_prefix + "Ray start commands", show_status=True):
                for cmd in self.ray_start_commands:
                    self.cmd_runner.run(cmd)