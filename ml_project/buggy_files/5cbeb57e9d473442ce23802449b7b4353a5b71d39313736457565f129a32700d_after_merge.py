    def exists(self, path_info):
        assert not isinstance(path_info, list)
        assert path_info.scheme == self.scheme
        return bool(self._request("HEAD", path_info.path))