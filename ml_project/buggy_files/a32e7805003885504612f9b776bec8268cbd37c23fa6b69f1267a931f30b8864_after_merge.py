    def garbage_collect_store(self, target_size_bytes: int) -> None:
        self._scheduler.garbage_collect_store(target_size_bytes)