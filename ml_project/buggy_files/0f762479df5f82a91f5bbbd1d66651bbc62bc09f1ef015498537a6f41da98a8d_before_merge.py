    def garbage_collect_store(self):
        self._native.lib.garbage_collect_store(self._scheduler)