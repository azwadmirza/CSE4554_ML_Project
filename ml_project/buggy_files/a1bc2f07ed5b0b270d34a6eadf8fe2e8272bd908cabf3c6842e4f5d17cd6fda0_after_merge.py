    def as_form_field(self):
        if self.value is None:
            return ''

        values = {}
        for key, value in self.value.items():
            if isinstance(value, (list, dict)):
                values[key] = value
            else:
                values[key] = '' if value is None else force_text(value)
        return self.__class__(self._field, values, self.errors, self._prefix)