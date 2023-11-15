def setup_task(cfg: DictConfig, **kwargs):
    task = None
    task_name = getattr(cfg, "task", None)

    if isinstance(task_name, str):
        # legacy tasks
        task = TASK_REGISTRY[task_name]
    else:
        task_name = getattr(cfg, "_name", None)

        if task_name and task_name in TASK_DATACLASS_REGISTRY:
            dc = TASK_DATACLASS_REGISTRY[task_name]
            cfg = merge_with_parent(dc(), cfg)
            task = TASK_REGISTRY[task_name]

    assert task is not None, f"Could not infer task type from {cfg}"

    return task.setup_task(cfg, **kwargs)