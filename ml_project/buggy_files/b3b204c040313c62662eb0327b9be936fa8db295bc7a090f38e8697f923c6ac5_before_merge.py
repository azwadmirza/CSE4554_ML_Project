    def get_link(self):
        target = "{0}#egg={1}".format(self.uri, self.name)
        return Link(target)