    def update_metadata(self):
        metadata_path = self.package_metadata()
        lockfile = metadata_path + ".lock"
        with fasteners.InterProcessLock(lockfile, logger=logger):
            lock_name = self.package_metadata()  # The path is the thing that defines mutex
            thread_lock = PackageCacheLayout._metadata_locks.setdefault(lock_name, threading.Lock())
            thread_lock.acquire()
            try:
                try:
                    metadata = self.load_metadata()
                except RecipeNotFoundException:
                    metadata = PackageMetadata()
                yield metadata
                save(metadata_path, metadata.dumps())
            finally:
                thread_lock.release()