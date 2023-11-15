        def key(item):
            field_val = getattr(item, self.field)
            if self.case_insensitive and isinstance(field_val, unicode):
                field_val = field_val.lower()
            return field_val