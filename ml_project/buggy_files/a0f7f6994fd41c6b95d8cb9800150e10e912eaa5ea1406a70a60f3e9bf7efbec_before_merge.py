    def _save_dir(self, path_info, tree, hash_info, save_link=True, **kwargs):
        dir_info = self.get_dir_cache(hash_info)
        for entry in Tqdm(
            dir_info, desc="Saving " + path_info.name, unit="file"
        ):
            entry_info = path_info / entry[self.tree.PARAM_RELPATH]
            entry_hash = HashInfo(
                self.tree.PARAM_CHECKSUM, entry[self.tree.PARAM_CHECKSUM]
            )
            self._save_file(
                entry_info, tree, entry_hash, save_link=False, **kwargs
            )

        if save_link:
            self.tree.state.save_link(path_info)
        if self.tree.exists(path_info):
            self.tree.state.save(path_info, hash_info.value)

        cache_info = self.tree.hash_to_path_info(hash_info.value)
        self.tree.state.save(cache_info, hash_info.value)