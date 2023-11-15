    def refresh(self):
        """
        Refresh context with new declarations from known registries.
        Useful for third-party extensions.
        """
        # Populate built-in registry
        from . import (arraymath, enumimpl, iterators, linalg, numbers,
                       optional, polynomial, rangeobj, slicing, tupleobj,
                       gdb_hook, hashing, heapq, literal)
        try:
            from . import npdatetime
        except NotImplementedError:
            pass
        self.install_registry(builtin_registry)
        self.load_additional_registries()
        # Also refresh typing context, since @overload declarations can
        # affect it.
        self.typing_context.refresh()