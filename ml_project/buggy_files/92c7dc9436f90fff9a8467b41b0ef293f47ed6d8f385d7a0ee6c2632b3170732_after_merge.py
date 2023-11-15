    def close_task(self, tid):
        """Close a task editor window."""

        try:
            editor = self.open_tasks[tid]
            editor.close()

            open_tasks = self.config.get("opened_tasks")

            if tid in open_tasks:
                open_tasks.remove(tid)

            self.config.set("opened_tasks", open_tasks)

        except KeyError:
            log.debug(f'Tried to close tid {tid} but it is not open')