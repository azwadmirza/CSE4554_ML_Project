    def serialize(self):
        if isinstance(self.link, UnboundType):
            name = self.link.name
        if isinstance(self.link, Instance):
            name = self.link.type.name()
        else:
            name = self.link.__class__.__name__
        # We should never get here since all forward references should be resolved
        # and removed during semantic analysis.
        assert False, "Internal error: Unresolved forward reference to {}".format(name)