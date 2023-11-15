    def __init__(
        self,
        stage,
        path,
        info=None,
        tree=None,
        cache=True,
        metric=False,
        plot=False,
        persist=False,
    ):
        self._validate_output_path(path, stage)
        # This output (and dependency) objects have too many paths/urls
        # here is a list and comments:
        #
        #   .def_path - path from definition in stage file
        #   .path_info - PathInfo/URLInfo structured resolved path
        #   .fspath - local only, resolved
        #   .__str__ - for presentation purposes, def_path/relpath
        #
        # By resolved path, which contains actual location,
        # should be absolute and don't contain remote:// refs.
        self.stage = stage
        self.repo = stage.repo if stage else None
        self.def_path = path
        self.info = info
        if tree:
            self.tree = tree
        else:
            self.tree = self.TREE_CLS(self.repo, {})
        self.use_cache = False if self.IS_DEPENDENCY else cache
        self.metric = False if self.IS_DEPENDENCY else metric
        self.plot = False if self.IS_DEPENDENCY else plot
        self.persist = persist

        self.path_info = self._parse_path(tree, path)
        if self.use_cache and self.cache is None:
            raise RemoteCacheRequiredError(self.path_info)