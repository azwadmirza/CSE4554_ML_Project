    def get_hash(self, path_info, tree=None, **kwargs):
        assert path_info and (
            isinstance(path_info, str) or path_info.scheme == self.scheme
        )

        if not tree:
            tree = self

        if not tree.exists(path_info):
            return None

        if tree == self:
            # pylint: disable=assignment-from-none
            hash_ = self.state.get(path_info)
        else:
            hash_ = None
        # If we have dir hash in state db, but dir cache file is lost,
        # then we need to recollect the dir via .get_dir_hash() call below,
        # see https://github.com/iterative/dvc/issues/2219 for context
        if (
            hash_
            and self.is_dir_hash(hash_)
            and not tree.exists(self.cache.tree.hash_to_path_info(hash_))
        ):
            hash_ = None

        if hash_:
            return hash_

        if tree.isdir(path_info):
            hash_ = self.get_dir_hash(path_info, tree, **kwargs)
        else:
            hash_ = tree.get_file_hash(path_info)

        if hash_ and self.exists(path_info):
            self.state.save(path_info, hash_)

        return hash_