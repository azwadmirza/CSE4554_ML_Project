    def on_key_release(self, event):
        """Called whenever key released in canvas.

        Parameters
        ----------
        event : qtpy.QtCore.QEvent
            Event from the Qt context.
        """
        if event.key is None:
            return
        combo = components_to_key_combo(event.key.name, event.modifiers)
        self.viewer.release_key(combo)