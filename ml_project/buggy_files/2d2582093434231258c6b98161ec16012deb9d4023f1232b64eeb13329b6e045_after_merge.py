    def commit_config(self, message=""):
        """Commit configuration."""
        commit_args = {"comment": message} if message else {}
        self.device.cu.commit(ignore_warning=self.ignore_warning, **commit_args)
        if not self.lock_disable and not self.session_config_lock:
            self._unlock()
        if self.config_private:
            self.device.rpc.close_configuration()