    def __getattr__(self, name):
        # When deepcopy is called, it creates and object without __init__,
        # self.parsed is not initialized and it causes infinite recursion.
        # More on this special casing here:
        # https://stackoverflow.com/a/47300262/298182
        if name.startswith("__"):
            raise AttributeError(name)
        return getattr(self.parsed, name)