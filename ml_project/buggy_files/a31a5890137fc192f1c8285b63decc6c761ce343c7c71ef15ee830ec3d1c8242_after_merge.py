    def is_activated(self, view):
        """Return True if package is activated."""
        if not self.is_extension:
            raise ValueError(
                "is_activated called on package that is not an extension.")
        if self.extendee_spec.package.installed_upstream:
            # If this extends an upstream package, it cannot be activated for
            # it. This bypasses construction of the extension map, which can
            # can fail when run in the context of a downstream Spack instance
            return False
        extensions_layout = view.extensions_layout
        exts = extensions_layout.extension_map(self.extendee_spec)
        return (self.name in exts) and (exts[self.name] == self.spec)