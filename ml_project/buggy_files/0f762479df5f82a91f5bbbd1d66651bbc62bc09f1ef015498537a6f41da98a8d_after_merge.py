    def garbage_collect_store(self, target_size_bytes: int) -> None:
        self._native.lib.garbage_collect_store(self._scheduler, target_size_bytes)