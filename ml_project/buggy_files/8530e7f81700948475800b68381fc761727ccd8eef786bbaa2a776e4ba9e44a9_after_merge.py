    def validate_none(self, object, name, value):
        if isinstance(value, object.__class__) or (value is None):
            return value

        self.error(object, name, value)