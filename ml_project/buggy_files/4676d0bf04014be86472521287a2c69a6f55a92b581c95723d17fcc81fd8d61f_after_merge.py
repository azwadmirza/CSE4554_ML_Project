    def lookup(self, name):
        # Look up name in this scope or an enclosing one.
        # Return None if not found.

        mangled_name = self.mangle_class_private_name(name)
        entry = (self.lookup_here(name)  # lookup here also does mangling
                or (self.outer_scope and self.outer_scope.lookup(mangled_name))
                or None)
        if entry:
            return entry

        # look up the original name in the outer scope
        # Not strictly Python behaviour but see https://github.com/cython/cython/issues/3544
        entry = (self.outer_scope and self.outer_scope.lookup(name)) or None
        if entry and entry.is_pyglobal:
            self._emit_class_private_warning(entry.pos, name)
        return entry