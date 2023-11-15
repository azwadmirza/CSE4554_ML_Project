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