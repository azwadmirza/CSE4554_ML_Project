    def current_window(self, keyctx):
        """
            Returns the active window, ignoring overlays.
        """
        t = self.focus_stack().top_window()
        if t.keyctx == keyctx:
            return t