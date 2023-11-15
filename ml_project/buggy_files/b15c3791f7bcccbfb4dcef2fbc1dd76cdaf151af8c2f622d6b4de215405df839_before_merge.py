    def rmdir(self, path=None):
        path = normalize_storage_path(path)
        if path:
            with self.lock:
                self.cursor.execute(
                    'DELETE FROM zarr WHERE k LIKE (? || "_%")', (path,)
                )
        else:
            self.clear()