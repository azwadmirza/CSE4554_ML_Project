def call(config: Any, *args: Any, **kwargs: Any) -> Any:
    """
    :param config: An object describing what to call and what params to use. needs to have a _target_ field.
    :param args: optional positional parameters pass-through
    :param kwargs: optional named parameters pass-through
    :return: the return value from the specified class or method
    """

    if OmegaConf.is_none(config):
        return None

    if isinstance(config, TargetConf) and config._target_ == "???":
        # Specific check to give a good warning about failure to annotate _target_ as a string.
        raise InstantiationException(
            f"Missing value for {type(config).__name__}._target_. Check that it's properly annotated and overridden."
            f"\nA common problem is forgetting to annotate _target_ as a string : '_target_: str = ...'"
        )

    if not (
        isinstance(config, dict)
        or OmegaConf.is_config(config)
        or is_structured_config(config)
    ):
        raise HydraException(f"Unsupported config type : {type(config).__name__}")

    # make a copy to ensure we do not change the provided object
    config_copy = OmegaConf.structured(config)
    if OmegaConf.is_config(config):
        config_copy._set_parent(config._get_parent())
    config = config_copy

    cls = "<unknown>"
    try:
        assert isinstance(config, DictConfig)
        OmegaConf.set_readonly(config, False)
        OmegaConf.set_struct(config, False)
        cls = _get_cls_name(config)
        type_or_callable = _locate(cls)
        if isinstance(type_or_callable, type):
            return _instantiate_class(type_or_callable, config, *args, **kwargs)
        else:
            assert callable(type_or_callable)
            return _call_callable(type_or_callable, config, *args, **kwargs)
    except InstantiationException as e:
        raise e
    except Exception as e:
        raise HydraException(f"Error calling '{cls}' : {e}") from e