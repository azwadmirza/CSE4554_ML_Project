    def delete_editor_task(self, action, params):
        """Callback to delete the task currently open."""

        editor = self.get_active_editor()
        task = editor.task

        if task.is_new():
            self.close_task(task.get_id(), editor.window)
        else:
            self.delete_tasks([task.get_id()], editor.window)