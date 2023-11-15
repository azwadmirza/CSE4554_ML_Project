    def serialize(self) -> JsonDict:
        return {
            'name': self.name,
            'is_in_init': self.is_in_init,
            'is_init_var': self.is_init_var,
            'has_default': self.has_default,
            'line': self.line,
            'column': self.column,
        }