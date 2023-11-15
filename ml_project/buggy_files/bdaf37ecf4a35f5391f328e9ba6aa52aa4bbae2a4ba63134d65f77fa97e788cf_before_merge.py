def _get_tasks_from_blocks(task_blocks: Sequence) -> Generator:
    """Get list of tasks from list made of tasks and nested tasks."""
    NESTED_TASK_KEYS = [
        'block',
        'always',
        'rescue',
    ]

    def get_nested_tasks(task: Any) -> Generator[Any, None, None]:
        return (
            subtask
            for k in NESTED_TASK_KEYS if task and k in task
            for subtask in task[k]
        )

    for task in task_blocks:
        for sub_task in get_nested_tasks(task):
            yield sub_task
        yield task