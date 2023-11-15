    def get_nested_tasks(task: Any) -> Generator[Any, None, None]:
        return (
            subtask
            for k in NESTED_TASK_KEYS if task and k in task
            for subtask in task[k]
        )