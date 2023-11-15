    def __setitem__(self, k, v):
        for obj in self.objs:
            if k in dir(obj):
                return setattr(self.objs[0], k, v)
        return setattr(self.objs[-1], k, v)