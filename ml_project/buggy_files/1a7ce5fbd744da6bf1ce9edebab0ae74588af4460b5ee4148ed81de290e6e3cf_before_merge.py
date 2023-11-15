    def current(self, keyctx):
        """
            Returns the active widget, but only the current focus or overlay has
            a matching key context.
        """
        t = self.focus_stack().top_widget()
        if t.keyctx == keyctx:
            return t