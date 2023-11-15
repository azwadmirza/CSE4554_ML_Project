    def joinpath(cls, localpath, *args):
        modified = cls(None, localpath)
        modified.path = modified.path.joinpath(*args)
        return modified