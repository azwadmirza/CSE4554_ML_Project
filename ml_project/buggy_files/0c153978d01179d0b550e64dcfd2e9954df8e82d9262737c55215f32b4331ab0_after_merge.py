def hydra_init(cfg_name="config") -> None:

    cs = ConfigStore.instance()
    cs.store(name=cfg_name, node=FairseqConfig)

    for k in FairseqConfig.__dataclass_fields__:
        v = FairseqConfig.__dataclass_fields__[k].default
        try:
            cs.store(name=k, node=v)
        except BaseException:
            logger.error(f"{k} - {v}")
            raise

    register_module_dataclass(cs, TASK_DATACLASS_REGISTRY, "task")
    register_module_dataclass(cs, MODEL_DATACLASS_REGISTRY, "model")

    for k, v in REGISTRIES.items():
        register_module_dataclass(cs, v["dataclass_registry"], k)