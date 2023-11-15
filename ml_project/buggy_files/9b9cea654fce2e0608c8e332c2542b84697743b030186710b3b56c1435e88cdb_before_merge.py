    def __call__(self):
        if self.is_update:
            raise SkipField()
        if callable(self.default):
            return self.default()
        return self.default