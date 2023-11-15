    def sync_file_mounts(self, sync_cmd, step_numbers=(0, 2)):
        # step_numbers is (# of previous steps, total steps)
        previous_steps, total_steps = step_numbers

        nolog_paths = []
        if cli_logger.verbosity == 0:
            nolog_paths = [
                "~/ray_bootstrap_key.pem", "~/ray_bootstrap_config.yaml"
            ]

        def do_sync(remote_path, local_path, allow_non_existing_paths=False):
            if allow_non_existing_paths and not os.path.exists(local_path):
                # Ignore missing source files. In the future we should support
                # the --delete-missing-args command to delete files that have
                # been removed
                return

            assert os.path.exists(local_path), local_path

            if os.path.isdir(local_path):
                if not local_path.endswith("/"):
                    local_path += "/"
                if not remote_path.endswith("/"):
                    remote_path += "/"

            with LogTimer(self.log_prefix +
                          "Synced {} to {}".format(local_path, remote_path)):
                self.cmd_runner.run("mkdir -p {}".format(
                    os.path.dirname(remote_path)))
                sync_cmd(local_path, remote_path)

                if remote_path not in nolog_paths:
                    # todo: timed here?
                    cli_logger.print("{} from {}", cf.bold(remote_path),
                                     cf.bold(local_path))

        # Rsync file mounts
        with cli_logger.group(
                "Processing file mounts",
                _numbered=("[]", previous_steps + 1, total_steps)):
            for remote_path, local_path in self.file_mounts.items():
                do_sync(remote_path, local_path)

        if self.cluster_synced_files:
            with cli_logger.group(
                    "Processing worker file mounts",
                    _numbered=("[]", previous_steps + 2, total_steps)):
                for path in self.cluster_synced_files:
                    do_sync(path, path, allow_non_existing_paths=True)
        else:
            cli_logger.print(
                "No worker file mounts to sync",
                _numbered=("[]", previous_steps + 2, total_steps))