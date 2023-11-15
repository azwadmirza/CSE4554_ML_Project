    def validate_none(self, object, name, value):
        if isinstance(value, object.__class__) or (value is None):
            return value

        self.validate_failed(object, name, value)