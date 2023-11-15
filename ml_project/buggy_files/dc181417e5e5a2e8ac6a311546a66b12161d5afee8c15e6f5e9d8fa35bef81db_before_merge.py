    def __init__(self, stage, path, info=None, remote=None):
        super(DependencyHTTP, self).__init__(
            stage, path, info=info, remote=remote
        )
        if path.startswith("remote"):
            path = urljoin(self.remote.cache_dir, urlparse(path).path)

        self.path_info = HTTPPathInfo(url=self.url, path=path)