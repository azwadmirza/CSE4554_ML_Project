    def get_dir_hash(self, path_info, **kwargs):
        dir_info = self._collect_dir(path_info, **kwargs)
        return self.repo.cache.local.save_dir_info(dir_info)