    def _get_relative_url(self, path: str) -> str:
        if not self.url:
            return ""
        suffix = str(self.template_path).replace(str(self.project_root), "")
        suffix_length = len(suffix.lstrip("/").split("/"))
        url_prefix = "/".join(self.url.split("/")[0:-suffix_length])
        suffix = str(path).replace(str(self.project_root), "")
        url = url_prefix + suffix
        return url