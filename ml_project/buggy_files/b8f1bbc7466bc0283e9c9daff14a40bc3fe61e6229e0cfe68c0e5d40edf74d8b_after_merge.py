    def mangle_class_private_name(self, name):
        # a few utilitycode names need to specifically be ignored
        if name and name.lower().startswith("__pyx_"):
            return name
        if name and name.startswith('__') and not name.endswith('__'):
            name = EncodedString('_%s%s' % (self.class_name.lstrip('_'), name))
        return name