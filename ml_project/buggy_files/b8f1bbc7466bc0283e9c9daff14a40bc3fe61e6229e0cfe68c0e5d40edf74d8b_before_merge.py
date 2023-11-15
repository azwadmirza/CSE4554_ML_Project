    def mangle_class_private_name(self, name):
        # a few utilitycode names need to specifically be ignored
        if name and name.lower().startswith("__pyx_"):
            return name
        return self.mangle_special_name(name)