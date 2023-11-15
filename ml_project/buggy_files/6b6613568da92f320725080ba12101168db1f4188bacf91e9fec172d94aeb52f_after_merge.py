    def url(self):
        return "{}://{}{}{}{}{}".format(
            self.scheme,
            self.netloc,
            self._spath,
            (";" + self.params) if self.params else "",
            ("?" + self.query) if self.query else "",
            ("#" + self.fragment) if self.fragment else "",
        )