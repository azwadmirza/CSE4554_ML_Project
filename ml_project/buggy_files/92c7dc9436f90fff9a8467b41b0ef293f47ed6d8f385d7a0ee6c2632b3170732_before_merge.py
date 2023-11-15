    def close_task(self, tid):
        """Close a task editor window."""

        if tid in self.open_tasks:
            editor = self.open_tasks[tid]

            # We have to remove the tid first, otherwise
            # close_task would be called once again
            # by editor.close
            del self.open_tasks[tid]

            editor.close()

            open_tasks = self.config.get("opened_tasks")

            if tid in open_tasks:
                open_tasks.remove(tid)

            self.config.set("opened_tasks", open_tasks)

        else:
            log.warn(f'Tried to close tid {tid} but it is not open')