    def sort(self, objs):
        # TODO: Conversion and null-detection here. In Python 3,
        # comparisons with None fail. We should also support flexible
        # attributes with different types without falling over.

        def key(item):
            field_val = item.get(self.field, '')
            if self.case_insensitive and isinstance(field_val, unicode):
                field_val = field_val.lower()
            return field_val

        return sorted(objs, key=key, reverse=not self.ascending)