    def lookup_here(self, name):
        # Look up in this scope only, return None if not found.
        name = self.mangle_class_private_name(name)
        return self.entries.get(name, None)