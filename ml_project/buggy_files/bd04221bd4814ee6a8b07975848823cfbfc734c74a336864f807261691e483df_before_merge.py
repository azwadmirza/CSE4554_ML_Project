    def box(self, instance, instance_type, val):
        if isinstance(val, string_types):
            val = val.replace(' ', ',').split(',')
        return super(_FeaturesField, self).box(instance, instance_type, val)