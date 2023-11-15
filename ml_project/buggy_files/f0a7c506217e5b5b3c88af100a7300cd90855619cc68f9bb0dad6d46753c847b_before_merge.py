    def __get__(self, obj, type=None):
        if obj is None:
            return self
        return obj.__dict__[self.field.name]