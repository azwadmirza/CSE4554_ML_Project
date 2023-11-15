    def start_plasma(self):
        from pyarrow import plasma
        self._plasma_store = plasma.start_plasma_store(
            self._cache_mem_limit, plasma_directory=self._plasma_dir)
        options.worker.plasma_socket, _ = self._plasma_store.__enter__()