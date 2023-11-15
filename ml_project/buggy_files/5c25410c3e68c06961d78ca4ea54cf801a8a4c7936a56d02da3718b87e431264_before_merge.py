    def discard_config(self):
        """Discard changes (rollback 0)."""
        self.device.cu.rollback(rb_id=0)
        if not self.lock_disable and not self.session_config_lock:
            self._unlock()