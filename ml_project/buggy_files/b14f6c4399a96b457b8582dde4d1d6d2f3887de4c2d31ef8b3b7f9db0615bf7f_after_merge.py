    def clear(self):
        self.mtime.clear()
        self.mtime_target.clear()
        self.size.clear()
        self.exists_local.clear()
        self.exists_remote.clear()
        self.has_inventory.clear()
        self.remaining_wait_time = self.max_wait_time