    def _convert(self, value):
        if isinstance(value, frozenset):
            return value
        elif not value:
            return frozenset()
        elif isinstance(value, string_types):
            return frozenset(value.replace(' ', ',').split(','))
        else:
            return frozenset(value)