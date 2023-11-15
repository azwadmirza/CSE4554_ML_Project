    def get_file_hash(self, path_info):
        """Return file checksum for specified path.

        If path_info is a DVC out, the pre-computed checksum for the file
        will be used. If path_info is a git file, MD5 will be computed for
        the git object.
        """
        if not self.exists(path_info):
            raise FileNotFoundError
        _, dvc_tree = self._get_tree_pair(path_info)
        if dvc_tree and dvc_tree.exists(path_info):
            try:
                return dvc_tree.get_file_hash(path_info)
            except OutputNotFoundError:
                pass
        return self.PARAM_CHECKSUM, file_md5(path_info, self)[0]