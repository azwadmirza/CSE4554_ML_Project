    def _get_checksum(self, locked=True):
        from dvc.repo.tree import RepoTree

        with self._make_repo(locked=locked) as repo:
            try:
                return repo.find_out_by_relpath(self.def_path).info["md5"]
            except OutputNotFoundError:
                path = PathInfo(os.path.join(repo.root_dir, self.def_path))

                # we want stream but not fetch, so DVC out directories are
                # walked, but dir contents is not fetched
                tree = RepoTree(repo, stream=True)

                # We are polluting our repo cache with some dir listing here
                if tree.isdir(path):
                    return self.repo.cache.local.get_hash(path, tree=tree)
                return tree.get_file_hash(path)