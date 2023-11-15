    def lookup_here(self, name):
        # Look up in this scope only, return None if not found.

        entry = self.entries.get(self.mangle_class_private_name(name), None)
        if entry:
            return entry
        # Also check the unmangled name in the current scope
        # (even if mangling should give us something else).
        # This is to support things like global __foo which makes a declaration for __foo
        return self.entries.get(name, None)