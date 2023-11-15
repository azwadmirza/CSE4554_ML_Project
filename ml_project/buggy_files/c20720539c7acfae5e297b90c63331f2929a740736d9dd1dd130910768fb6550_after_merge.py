    def run(self):
        cli_logger.old_info(logger, "{}Updating to {}", self.log_prefix,
                            self.runtime_hash)

        try:
            with LogTimer(self.log_prefix +
                          "Applied config {}".format(self.runtime_hash)):
                self.do_update()
        except Exception as e:
            error_str = str(e)
            if hasattr(e, "cmd"):
                error_str = "(Exit Status {}) {}".format(
                    e.returncode, " ".join(e.cmd))

            self.provider.set_node_tags(
                self.node_id, {TAG_RAY_NODE_STATUS: STATUS_UPDATE_FAILED})
            cli_logger.error("New status: {}", cf.bold(STATUS_UPDATE_FAILED))

            cli_logger.old_error(logger, "{}Error executing: {}\n",
                                 self.log_prefix, error_str)

            cli_logger.error("!!!")
            if hasattr(e, "cmd"):
                cli_logger.error(
                    "Setup command `{}` failed with exit code {}. stderr:",
                    cf.bold(e.cmd), e.returncode)
            else:
                cli_logger.verbose_error("{}", str(vars(e)))
                # todo: handle this better somehow?
                cli_logger.error("{}", str(e))
            # todo: print stderr here
            cli_logger.error("!!!")
            cli_logger.newline()

            if isinstance(e, click.ClickException):
                # todo: why do we ignore this here
                return
            raise

        tags_to_set = {
            TAG_RAY_NODE_STATUS: STATUS_UP_TO_DATE,
            TAG_RAY_RUNTIME_CONFIG: self.runtime_hash,
        }
        if self.file_mounts_contents_hash is not None:
            tags_to_set[
                TAG_RAY_FILE_MOUNTS_CONTENTS] = self.file_mounts_contents_hash

        self.provider.set_node_tags(self.node_id, tags_to_set)
        cli_logger.labeled_value("New status", STATUS_UP_TO_DATE)

        self.exitcode = 0