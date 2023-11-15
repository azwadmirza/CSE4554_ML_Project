    def lookup_target(self, name):
        # Look up name in this scope only. Declare as Python
        # variable if not found.
        entry = self.lookup_here(name)
        if not entry:
            entry = self.lookup_here_unmangled(name)
            if entry and entry.is_pyglobal:
                self._emit_class_private_warning(entry.pos, name)
        if not entry:
            entry = self.declare_var(name, py_object_type, None)
        return entry