    def save_dir_info(self, dir_info, hash_info=None):
        if hash_info and not self.changed_cache_file(hash_info):
            return hash_info

        hi, tmp_info = self._get_dir_info_hash(dir_info)
        if hash_info:
            assert hi == hash_info

        new_info = self.tree.hash_to_path_info(hi.value)
        if self.changed_cache_file(hi):
            self.tree.makedirs(new_info.parent)
            self.tree.move(tmp_info, new_info, mode=self.CACHE_MODE)

        self.tree.state.save(new_info, hi.value)

        return hi