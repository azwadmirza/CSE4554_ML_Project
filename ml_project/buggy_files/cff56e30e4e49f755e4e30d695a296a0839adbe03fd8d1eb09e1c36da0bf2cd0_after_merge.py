    def get_nested_tasks(task: Any) -> Generator[Any, None, None]:
        for k in NESTED_TASK_KEYS:
            if task and k in task and task[k]:
                for subtask in task[k]:
                    yield subtask