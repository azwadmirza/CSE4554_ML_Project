    def is_in_scope(self, node):
        """Determines whether or not the current node is in scope."""
        names, store = gather_load_store_names(node)
        names -= store
        if not names:
            return True
        inscope = False
        for ctx in reversed(self.contexts):
            names -= ctx
            if not names:
                inscope = True
                break
        return inscope