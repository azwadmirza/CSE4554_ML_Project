    def save_dir_info(self, dir_info):
        typ, hash_, tmp_info = self._get_dir_info_hash(dir_info)
        new_info = self.cache.tree.hash_to_path_info(hash_)
        if self.cache.changed_cache_file(hash_):
            self.cache.tree.makedirs(new_info.parent)
            self.cache.tree.move(
                tmp_info, new_info, mode=self.cache.CACHE_MODE
            )

        self.state.save(new_info, hash_)

        return typ, hash_