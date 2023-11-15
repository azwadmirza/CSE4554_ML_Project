    def validate(self, object, name, value):
        if isinstance(value, object.__class__):
            return value

        self.validate_failed(object, name, value)