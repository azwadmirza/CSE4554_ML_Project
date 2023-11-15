    def insert_existing_subtask(self, tid: str, line: int = None) -> None:
        """Insert an existing subtask in the buffer."""

        # Check if the task exists first
        if not self.req.has_task(tid):
            log.debug(f'Task {tid} not found')
            return

        if line is not None:
            start = self.buffer.get_iter_at_line(line)
        else:
            start = self.buffer.get_end_iter()
            self.buffer.insert(start, '\n')
            start.forward_line()
            line = start.get_line()

        # Add subtask name
        task = self.req.get_task(tid)
        self.buffer.insert(start, task.get_title())

        # Reset iterator
        start = self.buffer.get_iter_at_line(line)

        # Add checkbox
        self.add_checkbox(tid, start)

        # Apply link to subtask text
        end = start.copy()
        end.forward_to_line_end()

        link_tag = InternalLinkTag(tid, task.get_status())
        self.table.add(link_tag)
        self.buffer.apply_tag(link_tag, start, end)
        self.tags_applied.append(link_tag)

        # Apply subtask tag to everything
        start.backward_char()
        subtask_tag = SubTaskTag(tid)
        self.table.add(subtask_tag)
        self.buffer.apply_tag(subtask_tag, start, end)

        self.subtasks['tags'].append(tid)