    def _get_relative_url(self, path: str) -> str:
        suffix = str(path).replace(str(self.project_root), "")
        url = self.url_prefix() + suffix
        return url