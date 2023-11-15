def setup_task(cfg: DictConfig, **kwargs):
    if isinstance(cfg, DictConfig):
        return TASK_REGISTRY[cfg._name].setup_task(cfg, **kwargs)
    return TASK_REGISTRY[cfg.task].setup_task(cfg, **kwargs)