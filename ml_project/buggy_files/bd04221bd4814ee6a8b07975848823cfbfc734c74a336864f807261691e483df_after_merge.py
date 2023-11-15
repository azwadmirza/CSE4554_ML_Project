    def box(self, instance, instance_type, val):
        if isinstance(val, string_types):
            val = val.replace(' ', ',').split(',')
        val = tuple(f for f in (ff.strip() for ff in val) if f)
        return super(_FeaturesField, self).box(instance, instance_type, val)