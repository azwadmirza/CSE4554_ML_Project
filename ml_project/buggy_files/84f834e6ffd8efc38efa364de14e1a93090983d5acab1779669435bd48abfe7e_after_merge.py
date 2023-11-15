    def save_dir_info(self, dir_info):
        hash_info, tmp_info = self._get_dir_info_hash(dir_info)
        new_info = self.cache.tree.hash_to_path_info(hash_info.value)
        if self.cache.changed_cache_file(hash_info.value):
            self.cache.tree.makedirs(new_info.parent)
            self.cache.tree.move(
                tmp_info, new_info, mode=self.cache.CACHE_MODE
            )

        self.state.save(new_info, hash_info.value)

        return hash_info