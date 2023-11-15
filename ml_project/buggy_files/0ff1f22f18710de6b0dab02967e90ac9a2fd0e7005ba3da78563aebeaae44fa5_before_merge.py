    def _get_lock(self, key):
        """Create a lock for a key, if necessary, and return a lock object."""
        if key not in self._locks:
            lock_file = self._lock_path(key)
            if not os.path.exists(lock_file):
                touch(lock_file)
            self._locks[key] = Lock(lock_file)
        return self._locks[key]