    def _resolve_type(self, value, _type):
        return type_map[self._type_definition.name].implementation