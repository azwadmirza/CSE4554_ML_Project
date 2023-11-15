    def wait_ready(self, deadline):
        with cli_logger.group(
                "Waiting for SSH to become available", _numbered=("[]", 1, 6)):
            with LogTimer(self.log_prefix + "Got remote shell"):
                cli_logger.old_info(logger, "{}Waiting for remote shell...",
                                    self.log_prefix)

                cli_logger.print("Running `{}` as a test.", cf.bold("uptime"))
                first_conn_refused_time = None
                while time.time() < deadline and \
                        not self.provider.is_terminated(self.node_id):
                    try:
                        cli_logger.old_debug(logger,
                                             "{}Waiting for remote shell...",
                                             self.log_prefix)

                        self.cmd_runner.run("uptime", run_env="host")
                        cli_logger.old_debug(logger, "Uptime succeeded.")
                        cli_logger.success("Success.")
                        return True
                    except ProcessRunnerError as e:
                        first_conn_refused_time = \
                            cmd_output_util.handle_ssh_fails(
                                e, first_conn_refused_time,
                                retry_interval=READY_CHECK_INTERVAL)
                        time.sleep(READY_CHECK_INTERVAL)
                    except Exception as e:
                        # TODO(maximsmol): we should not be ignoring
                        # exceptions if they get filtered properly
                        # (new style log + non-interactive shells)
                        #
                        # however threading this configuration state
                        # is a pain and I'm leaving it for later

                        retry_str = str(e)
                        if hasattr(e, "cmd"):
                            retry_str = "(Exit Status {}): {}".format(
                                e.returncode, " ".join(e.cmd))

                        cli_logger.print(
                            "SSH still not available {}, "
                            "retrying in {} seconds.", cf.gray(retry_str),
                            cf.bold(str(READY_CHECK_INTERVAL)))
                        cli_logger.old_debug(logger,
                                             "{}Node not up, retrying: {}",
                                             self.log_prefix, retry_str)

                        time.sleep(READY_CHECK_INTERVAL)

        assert False, "Unable to connect to node"