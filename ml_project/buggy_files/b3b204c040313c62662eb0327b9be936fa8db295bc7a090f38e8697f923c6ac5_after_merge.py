    def get_link(self):
        target = "{0}#egg={1}".format(self.uri, self.name)
        link = Link(target)
        if link.is_wheel and self._has_hashed_name:
            self.name = os.path.basename(Wheel(link.path).name)
        return link