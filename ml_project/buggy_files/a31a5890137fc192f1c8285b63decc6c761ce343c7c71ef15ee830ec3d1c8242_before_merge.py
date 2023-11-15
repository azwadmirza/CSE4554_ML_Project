    def is_activated(self, view):
        """Return True if package is activated."""
        if not self.is_extension:
            raise ValueError(
                "is_activated called on package that is not an extension.")
        extensions_layout = view.extensions_layout
        exts = extensions_layout.extension_map(self.extendee_spec)
        return (self.name in exts) and (exts[self.name] == self.spec)