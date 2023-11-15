    def current(self, keyctx):
        """
        Returns the active widget with a matching key context, including overlays.
        If multiple stacks have an active widget with a matching key context,
        the currently focused stack is preferred.
        """
        for s in self.stacks_sorted_by_focus():
            t = s.top_widget()
            if t.keyctx == keyctx:
                return t