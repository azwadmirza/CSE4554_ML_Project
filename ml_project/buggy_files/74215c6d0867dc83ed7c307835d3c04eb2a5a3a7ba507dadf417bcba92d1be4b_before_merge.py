    def pre_destroy(self):
        self._heartbeat_ref.destroy()
        super().pre_destroy()