    def monitor(self, path):
        mod_time = None
        if os.path.exists(path):
            mod_time = time.ctime(os.path.getmtime(path))
        with self._lock:
            self.paths[path] = mod_time
        self.start()