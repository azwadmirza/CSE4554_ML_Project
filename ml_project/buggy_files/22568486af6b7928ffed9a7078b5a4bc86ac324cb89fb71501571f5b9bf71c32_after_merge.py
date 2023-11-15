    def from_error(cls, update, error, dispatcher, async_args=None, async_kwargs=None):
        self = cls.from_update(update, dispatcher)
        self.error = error
        self.async_args = async_args
        self.async_kwargs = async_kwargs
        return self