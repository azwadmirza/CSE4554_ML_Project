    def collect_errors(self, instance, value, source="<<merged>>"):
        errors = super(MapParameter, self).collect_errors(instance, value)
        element_type = self._element_type
        errors.extend(InvalidElementTypeError(self.name, val, source, type(val), element_type, key)
                      for key, val in iteritems(value) if not isinstance(val, element_type))
        return errors