    def joinpath(cls, *args):
        modified = cls(None)
        modified.path = modified.path.joinpath(*args)
        return modified