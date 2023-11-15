    def get_requirement(self):
        prefix = "-e " if self.editable else ""
        line = "{0}{1}".format(prefix, self.link.url)
        req = first(requirements.parse(line))
        if self.path and self.link and self.link.scheme.startswith("file"):
            req.local_file = True
            req.path = self.path
            req.uri = None
            self._uri_scheme = "file"
        if self.editable:
            req.editable = True
        req.link = self.link
        return req