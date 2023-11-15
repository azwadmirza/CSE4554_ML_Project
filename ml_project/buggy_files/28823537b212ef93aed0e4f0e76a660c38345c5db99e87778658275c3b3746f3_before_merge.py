    def __getitem__(self, k):
        for obj in self.objs:
            if k in dir(obj):
                return getattr(obj, k)
        raise KeyError(k)