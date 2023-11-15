    def keys(self):
        return list(sum(set(dir(obj)) for obj in objs))