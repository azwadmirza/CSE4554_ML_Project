    def lookup(self, name):
        # Look up name in this scope or an enclosing one.
        # Return None if not found.
        name = self.mangle_class_private_name(name)
        return (self.lookup_here(name)
            or (self.outer_scope and self.outer_scope.lookup(name))
            or None)