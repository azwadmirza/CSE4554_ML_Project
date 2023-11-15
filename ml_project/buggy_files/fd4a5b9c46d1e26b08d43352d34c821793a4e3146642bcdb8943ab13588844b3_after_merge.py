    def add_task(self, task: Task) -> Task:
        """
        Add a task to the flow if the task does not already exist. The tasks are
        uniquely identified by their `slug`.

        Args:
            - task (Task): the new Task to be added to the flow

        Returns:
            - Task: the `Task` object passed in if the task was successfully added

        Raises:
            - TypeError: if the `task` is not of type `Task`
            - ValueError: if the `task.slug` matches that of a task already in the flow
        """
        if not isinstance(task, Task):
            raise TypeError(
                "Tasks must be Task instances (received {})".format(type(task))
            )
        elif task not in self.tasks:
            if task.slug and any(task.slug == t.slug for t in self.tasks):
                raise ValueError(
                    'A task with the slug "{}" already exists in this '
                    "flow.".format(task.slug)
                )

            self.tasks.add(task)
            self._cache.clear()

            # Parameters must be root tasks
            # All other new tasks should be added to the current case (if any)
            if not isinstance(task, Parameter):
                case = prefect.context.get("case", None)
                if case is not None:
                    case.add_task(task, self)

        return task