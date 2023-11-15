    def get_requirement(self):
        base = "{0}".format(self.link)
        req = first(requirements.parse(base))
        if self.editable:
            req.editable = True
        if self.link and self.link.scheme.startswith("file"):
            if self.path:
                req.path = self.path
                req.local_file = True
                self._uri_scheme = "file"
                req.uri = None
        req.link = self.link
        return req