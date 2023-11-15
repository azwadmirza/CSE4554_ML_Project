    def box(self, instance, val):
        if isinstance(val, string_types):
            val = val.replace('-', '').replace('_', '').lower()
        return super(LinkTypeField, self).box(instance, val)