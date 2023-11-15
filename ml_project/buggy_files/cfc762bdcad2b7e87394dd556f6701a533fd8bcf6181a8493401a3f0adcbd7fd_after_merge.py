    def _convert(self, value):
        if not value:
            return frozenset()
        elif isinstance(value, string_types):
            return frozenset(f for f in (
                ff.strip() for ff in value.replace(' ', ',').split(',')
            ) if f)
        else:
            return frozenset(f for f in (ff.strip() for ff in value) if f)