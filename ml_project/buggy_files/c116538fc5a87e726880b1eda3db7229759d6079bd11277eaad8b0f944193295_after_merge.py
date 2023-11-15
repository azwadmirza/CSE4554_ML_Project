def build_model(cfg: DictConfig, task):

    model = None
    model_type = getattr(cfg, "_name", None) or getattr(cfg, "arch", None)

    if not model_type and len(cfg) == 1:
        # this is hit if config object is nested in directory that is named after model type

        model_type = next(iter(cfg))
        if model_type in MODEL_DATACLASS_REGISTRY:
            cfg = cfg[model_type]
        else:
            raise Exception(
                "Could not infer model type from directory. Please add _name field to indicate model type"
            )

    if model_type in ARCH_MODEL_REGISTRY:
        # case 1: legacy models
        model = ARCH_MODEL_REGISTRY[model_type]
    elif model_type in MODEL_DATACLASS_REGISTRY:
        # case 2: config-driven models
        model = MODEL_REGISTRY[model_type]

    if model_type in MODEL_DATACLASS_REGISTRY:
        # set defaults from dataclass. note that arch name and model name can be the same
        dc = MODEL_DATACLASS_REGISTRY[model_type]
        cfg = merge_with_parent(dc(), cfg)

    assert model is not None, f"Could not infer model type from {cfg}"

    return model.build_model(cfg, task)