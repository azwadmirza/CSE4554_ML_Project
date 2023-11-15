    def get_editorstack(self):
        """Get the current editorstack."""
        plugin = self.ipyclient.plugin
        if plugin.main.editor is not None:
            editor = plugin.main.editor
            return editor.get_current_editorstack()
        raise RuntimeError('No editorstack found.')