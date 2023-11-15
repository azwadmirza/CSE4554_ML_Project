    def close_focused_task(self, action, params):
        """Callback to close currently focused task editor."""

        if self.open_tasks:
            tid = self.get_active_editor().task.get_id()
            self.close_task(tid)