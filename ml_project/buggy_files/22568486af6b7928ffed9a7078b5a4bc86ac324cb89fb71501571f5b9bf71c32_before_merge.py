    def from_error(cls, update, error, dispatcher):
        self = cls.from_update(update, dispatcher)
        self.error = error
        return self