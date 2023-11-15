    def __setitem__(self, k, v):
        for obj in self.objs:
            if k in dir(obj):
                return setattr(obj, k, v)
        self.locals[k] = v