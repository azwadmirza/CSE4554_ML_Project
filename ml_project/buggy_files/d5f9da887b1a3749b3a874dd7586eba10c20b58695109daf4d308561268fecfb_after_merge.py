    def validate(self, object, name, value):
        if isinstance(value, object.__class__):
            return value

        self.error(object, name, value)