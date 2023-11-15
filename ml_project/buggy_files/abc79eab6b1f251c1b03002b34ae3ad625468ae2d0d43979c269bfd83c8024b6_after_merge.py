    def get_dir_hash(self, path_info, **kwargs):
        if not self.cache:
            raise RemoteCacheRequiredError(path_info)

        dir_info = self._collect_dir(path_info, **kwargs)
        return self.cache.save_dir_info(dir_info)