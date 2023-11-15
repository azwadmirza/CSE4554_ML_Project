    def close_focused_task(self, action, params):
        """Callback to close currently focused task editor."""

        editor = self.get_active_editor()

        if editor:
            self.close_task(editor.task.get_id())