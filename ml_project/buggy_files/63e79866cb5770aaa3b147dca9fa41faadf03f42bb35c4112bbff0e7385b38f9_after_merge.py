    def open(
        self, path, mode="r", encoding="utf-8", **kwargs
    ):  # pylint: disable=arguments-differ
        if "b" in mode:
            encoding = None

        tree, dvc_tree = self._get_tree_pair(path)
        path_info = PathInfo(path)
        try:
            return tree.open(path_info, mode=mode, encoding=encoding)
        except FileNotFoundError:
            if not dvc_tree:
                raise

        return dvc_tree.open(path_info, mode=mode, encoding=encoding, **kwargs)