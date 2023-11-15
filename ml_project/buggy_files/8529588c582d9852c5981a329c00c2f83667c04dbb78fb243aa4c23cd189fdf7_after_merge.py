    def __getattr__(self, name):
        try:
            return super().__getattr__(name)
        except AttributeError as e:
            try:
                return super().__getattribute__(name)
            except AttributeError:
                raise e