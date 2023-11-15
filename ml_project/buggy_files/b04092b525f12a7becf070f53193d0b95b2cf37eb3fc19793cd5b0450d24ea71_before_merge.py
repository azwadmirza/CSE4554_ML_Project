    def run_rsync_down(self, source, target, redirect=None):
        if target.startswith("~"):
            target = "/root" + target[1:]

        try:
            self.process_runner.check_call(
                [
                    KUBECTL_RSYNC,
                    "-avz",
                    "{}@{}:{}".format(self.node_id, self.namespace, source),
                    target,
                ],
                stdout=redirect,
                stderr=redirect)
        except Exception as e:
            logger.warning(self.log_prefix +
                           "rsync failed: '{}'. Falling back to 'kubectl cp'"
                           .format(e))
            self.process_runner.check_call(
                self.kubectl + [
                    "cp", "{}/{}:{}".format(self.namespace, self.node_id,
                                            source), target
                ],
                stdout=redirect,
                stderr=redirect)