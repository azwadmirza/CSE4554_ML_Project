    def destruction(self, _=None):
        """Callback when destroying the window."""

        # Save should be also called when buffer is modified
        self.pengine.onTaskClose(self.plugin_api)
        self.pengine.remove_api(self.plugin_api)

        tid = self.task.get_id()

        if self.task.is_new():
            self.req.delete_task(tid)
        else:
            self.save()
            [sub.set_to_keep() for sub in self.task.get_subtasks() if sub]

        try:
            del self.app.open_tasks[tid]
        except KeyError:
            log.debug(f'Task {tid} was already removed from the open list')