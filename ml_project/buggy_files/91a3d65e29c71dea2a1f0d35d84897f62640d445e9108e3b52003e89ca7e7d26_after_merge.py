    def get_hash(self, path_info, **kwargs):
        assert path_info and (
            isinstance(path_info, str) or path_info.scheme == self.scheme
        )

        if not self.exists(path_info):
            return None

        # pylint: disable=assignment-from-none
        hash_ = self.state.get(path_info)

        # If we have dir hash in state db, but dir cache file is lost,
        # then we need to recollect the dir via .get_dir_hash() call below,
        # see https://github.com/iterative/dvc/issues/2219 for context
        if (
            hash_
            and self.is_dir_hash(hash_)
            and not self.cache.tree.exists(
                self.cache.tree.hash_to_path_info(hash_)
            )
        ):
            hash_ = None

        if hash_:
            hash_info = HashInfo(self.PARAM_CHECKSUM, hash_)
            if hash_info.isdir:
                hash_info.dir_info = self.cache.get_dir_cache(hash_info)
            return hash_info

        if self.isdir(path_info):
            hash_info = self.get_dir_hash(path_info, **kwargs)
        else:
            hash_info = self.get_file_hash(path_info)

        if hash_info and self.exists(path_info):
            self.state.save(path_info, hash_info.value)

        return hash_info