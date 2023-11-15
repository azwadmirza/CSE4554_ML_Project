def build_model(cfg: DictConfig, task):
    if isinstance(cfg, DictConfig):
        return ARCH_MODEL_REGISTRY[cfg._name].build_model(cfg, task)
    return ARCH_MODEL_REGISTRY[cfg.arch].build_model(cfg, task)